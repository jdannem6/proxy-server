### Socket Programming Project 2
### Written by Justin Dannemiller
### CS 35201: Computer Communication Networks
### 28 May 2022

from distutils.debug import DEBUG
import socket
import datetime
from datetime import date
from sqlalchemy import false, true
import os # module used for directories
import pathlib # necessary for creating cache directories
from io import BytesIO
import gzip

# Constants of proxy server identity
# set Proxy to the name of device running this applicaition
PROXY = socket.gethostbyname(socket.gethostname())
PROXY_PORT = 8880 # port number of proxy server
PROXY_ADDRESS = (PROXY, PROXY_PORT)

# Constants for requests/responses
HEADER_SIZE = 16
TEXT_FORMAT = 'utf-8'
MSG_SIZE = 4096
DEBUG_MODE = False # True if you wish to display headers of all requests
                  # and responses; false otherwise
REQUIRED_REQUESTS = 100
SERVER_PORT = 80

# Creates a header for responses sent back to the client (browser)
def getResponseHeader():
    response = 'HTTP/1.0 200 OK\n'
    response += 'Vary: Accept/Encoding\n'
    response += 'Content-Type: text/html\n'

    # Get time and date information
    date = datetime.datetime.now()
    formatted_date = str(date.day) + "/" + str(date.month) +  "/" 
    formatted_date += str(date.year) + "    " + str(date.hour) + ":" 
    formatted_date += str(date.minute) + ":" + str(date.second) + " EST"
    response += 'Date: ' + formatted_date + '\n'

    response += 'Last-Modified: 04/28/2022\n'
    response += 'Server: localhost\n\n'
    return response

# Forwards requests sent by the client (browser) to the server
def forwardRequest(server_name):
    # Get server address
    server_address = socket.gethostbyname(server_name)
    # Create socket for connection with server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect with server
    server_socket.connect((server_address, SERVER_PORT))
    # Forward request to server
    server_socket.sendall(request.encode())
    # Receive response from server
    server_socket.settimeout(1)
    try:
        response = b''
        while True:
            segment = server_socket.recv(MSG_SIZE)
            if not segment:
                break
            response += segment
        return response
    except:
        return response
# Returns a string containing the usage data for all the requests      
def printUsageTable():

    # After each request, print the network usage information
    table_header = "Total requests | Total bytes of all requests |"
    table_header += " Total number of cache hits | Total bytes of all cache hits\n"
    table_content = "\t" + str(total_requests) + "\t\t" + str(total_bytes) + "\t\t\t\t" + str(cache_hits) + "\t\t\t\t" + str(cache_bytes)
    table = table_header + table_content
    print(table)

# Returns a string containing the html formatted usage data
def getUsageLog():
    usage_info = "<h>Usage Log<h>"
    usage_info += "<div>Total Requests: " + str(total_requests) +" | "
    usage_info += "Total requests bytes: " + str(total_bytes) + " | "
    usage_info += "Cache hits: " + str(cache_hits) + " | " 
    usage_info += "Total cache bytes: " + str(cache_bytes)  + "</div>"

    return usage_info


if __name__ == "__main__":
    
    # Initialize web_cache as empty dictionary of dictionaries
    web_cache = dict()

    # Network usage trackers
    total_requests = 0 
    total_bytes = 0 # Total bytes sent in serving of requests
    cache_hits = 0
    cache_bytes = 0 # Total number of bytes in cache hits

    # Establish socket for TCP connection with clients
    proxy_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow the proxy's address to be reused
    proxy_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind the proxy's socket to its address and port
    proxy_server.bind(PROXY_ADDRESS)

    # Listen for up to 100 http requests from clients
    proxy_server.listen(REQUIRED_REQUESTS)
    print("Server started http://%s:%s" % (PROXY, PROXY_PORT))

    connected = True # True while the proxy is connected to the user
    while (connected):

        
        # wait for client to establish connection. Once connection is 
        # received, save the client address and connection object (they are
        # needed for the reponse)
        client_connection, client_address = proxy_server.accept()

        # Get a request from client
        request = client_connection.recv(MSG_SIZE).decode()
        # increment request count
        total_requests += 1
        
        

        # Parse the request to get the information within the header
        segmented_request = request.split("\n") # splits request line-by-line
        # First line in request corresponds to header
        header = segmented_request[0]
        # Determine the type of request
        # First, split the request header into its parts
        header_segments = header.split(" ")
        request_type = header_segments[0]

        if (request_type == "GET"):
            # Print the contents of the request (DEBUG_MODE)
            if DEBUG_MODE: print("[Request]: \n" + request + "\n")

            # If client requests proxy usage page, print proxy usage data
            if (header_segments[1] == "/proxy_usage?"):
                usage_info = getUsageLog()
                #usage_table = getUsageTable()
                header = getResponseHeader()
                response = header + usage_info
                client_connection.send(response.encode())
            
            # If client wants to reset proxy usage data, do so and send them
            # the result
            elif (header_segments[1] == "/proxy_usage_reset?"):
                # First reset all the usage trackers to 0
                total_requests = 0
                total_bytes = 0
                cache_hits = 0
                cache_bytes = 0

                # Now get the usage table
                usage_info = getUsageLog()

                # Send the newly reset usage data to user
                header = getResponseHeader()
                response = header + usage_info
                client_connection.send(response.encode())


            # Otherwise, if the client requests a file from a server
            elif ("http://" in header_segments[1]):
            # Get server name and file name
                            # Get requested URL from header
                server_URL = header_segments[1]
                segmented_URL = server_URL.split("/")
                server_name = segmented_URL[2] # The server name occurs after the 
                                               # second forward slash (e.g. 
                                               # https://server.com)
                file_name = segmented_URL[-1] # file name occurs after last forward slash
                if file_name == server_name:
                    continue
                file_path = server_name + "/" + file_name
        

                ## Try to access the requested file
                # if the corresponding cache directory exists, look for the file
                if (server_name in web_cache):
                    # if the requested file exists within the cache directory, send a 
                    # response to the user with the contents of that file
                    if (file_name in web_cache[server_name]):
                        print("Cache Hit!")
                        cache_miss = False
                        cache_hits += 1
                        ## Send the contents of the file to the client
                        # Get content from dictionary
                        content = web_cache[server_name][file_name] 
                        # Forward the file to client
                        client_connection.sendall(content)

                        ## Update cache and total byte tracker
                        # Segment the response into its header fields and content
                        segmented_response = content.split(b'\r\n\r\n')
                        header = segmented_response[0]
                        payload = segmented_response[1]

                        header_text = str(segmented_response[0], TEXT_FORMAT)
                        seg_header = header_text.split("\r\n")

                        ## Update byte totals
                        for header_line in seg_header:
                            if ("Content-Length:" in header_line):
                                bytes_in_response = int(header_line.split()[1])
                        total_bytes += len(content)
                        cache_bytes += len(content)
                
                    # otherwise if the file doesn't exist, it was a cache miss
                    else: 
                        cache_miss = True
                # Otherwise, if the cache directory doesn't exist, it was a cache miss
                else:
                    cache_miss = True

                # If the request resulted in a cache miss, forward the request to the 
                # server
                if (cache_miss):
                    #server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    print("Cache Miss!")
                    server_response = forwardRequest(server_name) 

                    # Segment the response into its header fields and content
                    segmented_response = server_response.split(b'\r\n\r\n')
                    header = segmented_response[0]
                    payload = segmented_response[1]
                
                    header_text = str(segmented_response[0], TEXT_FORMAT)
                    seg_header = header_text.split("\r\n")

                    ## Update byte totals
                    for header_line in seg_header:
                        if ("Content-Length:" in header_line):
                            bytes_in_response = header_line.split()[1]
                            bytes_in_response = int(bytes_in_response)
                
                    total_bytes += len(server_response)

                
                    # Prints response information
                    if DEBUG_MODE:
                        # Print all header fields within the response message
                        print("[Response Header:]")
                        for line in seg_header:
                            print(line)

                    # Get the status code from the response message
                    first_line = seg_header[0]
                    status_code = first_line.split()[1]
                    # If the status_code of the response message is 200, the file exists
                    # Store the file in the web_cache and then forward it to client
                    if  (status_code == "200"):
                        ## Cache payload of the response
                        # If there is not yet a cache for the given server
                        # create a dictionary for it
                        if (server_name not in web_cache):
                            web_cache[server_name] = dict()

                        # In either case, place the payload of the response in the 
                        # corresponding file of the server's cache
                        web_cache[server_name][file_name] = server_response

                        # Forward the file to client
                        client_connection.sendall(server_response)

                    # Otherwise, if the status_code of the response message is
                    # 404, the requested file does not exist. Send 404 error message
                    # to client
                    elif(status_code == "404"):
                        response_header = "HTTP/1.0 404 NOT FOUND\n\n" 
                        response = response_header + "<h1>404 Error: File Not Found</h1>"
                        response += "\n <h2>Whoopsie!</h2> \nThe page you are trying to reach does"
                        response += " not exist! Return to previous page"

                        client_connection.sendall(response.encode())

            # Otherwise, if the final can not be found return 404 error
            else:
                response_header = "HTTP/1.0 404 NOT FOUND\n\n" 
                response = response_header + "<h1>404 Error: File Not Found</h1>"
                response += "\n <h2>Whoopsie!</h2> \nThe page you are trying to reach does"
                response += " not exist! Return to previous page"

                client_connection.sendall(response.encode())

        # After each request, print the network usage information
        printUsageTable()
        client_connection.close()
    proxy_server.close()
 
            


            


