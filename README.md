# Proxy Server Project
### CS35201: Computer Communication Networks
This project emulates a simple proxy server which can serve up to 100 client requests.


## Program Description
The proxy server parses client requests to determine the file and server they are requesting. If the requested file is in the proxy's cache, it is sent directly to the client. Otherwise, the proxy retrieves the requested file from the origin server, caches it, adn forwards the file to the client. This program effectively demonstrates the utility of a proxy server in limiting the network usage of a set of hosts in a LAN.

### Prerequisites
This project was tested and run with Python3.9.12 and an Ubuntu 20.04.04 LTS operating system.

## Installation
1. Clone the repository

![](/Documentation_Images/repo_cloning.png)
## Program Interpretation and Execution
1. Run the proxy_server.py file:

![](/Documentation_Images/ProgramRun.png)

2. Visit the URLs listed below to request the corresponding files from the proxy server

URLs: 
http://gaia.atr.cs.kent.edu/proxy_test1.html 
http://gaia.atr.cs.kent.edu/proxy_test2.html 
http://gaia.atr.cs.kent.edu/proxy_test3.html 

3. To print the network usage information, visit the link output by the program. This link is the first line printed by the program, as shown below.
![](/Documentation_Images/usage_link.png)

At that link, the webpage should look as shown below:
![](/Documentation_Images/proxy_usage.png)

4. To reset the proxy usage information, visit the same link as above, but replace proxy_usage? with proxy_usage_reset?. This page should look as shown below:
![](/Documentation_Images/proxy_reset.png)


## Example Output
![](/Documentation_Images/sample_output.png)

### Suggestions for Running and Testing Program
1. For increased feedback, the program includes a debug mode which can be used to toggle the printing of HTTP response and request headers. By default, the program is not in debug mode. To change it to debug mode, set the DEBUG_MODE constant to True:

![](/Documentation_Images/DebugMode.png)

2. Visit the provided websites while in Incognito Mode to prevent your browser cache from interfering with the proxy. Moreover, after a given file has been requested from a server, and you would like to request it again, you must close the entire Incognito Mode window and revisit the corresponding URL in a new Incognito Window. Otherwise, the browser's cache interferes with the caching in the proxy server program.
 

