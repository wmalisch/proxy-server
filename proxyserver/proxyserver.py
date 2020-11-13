import socket
import os
import datetime
import signal
import sys

PORT = 8080
BUFFER_SIZE = 1024 # bytes
EXPIRY = 30 # Second

# Signal handler for graceful exiting.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)

def prepare_get_message(line1, line2):
    request = line1 + line2
    return request



# Read a single line (ending with \n) from a socket and return it.
# We will strip out the \r and the \n in the process.
def get_line_from_socket(sock):
    done = False
    line = ''
    while(not done):
        char = sock.recv(1).decode()
        if (char == '\r'):
            pass
        elif(char == '\n'):
            done = True
        else:
            line = line + char
    return line

def send_response_to_client(sock, code, file_name):
    ##################################
    # WRITE CODE TO SEND RESPONSE HERE
    ##################################

# Our main function.

def main():

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Create the socket.  We will ask this to work on any interface and to pick
    # a free port at random.  We'll print this out for clients to use.

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', PORT))
    print('Will wait for client connections at port ' + str(server_socket.getsockname()[1]))
    server_socket.listen(1)
    
    # Keep the server running forever.
    
    while(1):
        print('Waiting for incoming client connection ...')
        conn, addr = server_socket.accept()
        print('Accepted connection from client address: ', addr)
        print('Connection to client established, waiting to receive a message ...')
       
        request = get_line_from_socket(conn)
        server_info = get_line_from_socket(conn)
        server = server_info.split()[1].partition(':')
        
        print('\nReceived request: ' + request)
        print('Main server host received: ',server[0])
        print('Main server listening on port: ' + server[2] + '\n')
        request_list = request.split()

        ########################################################################
        # THIS WILL REMOVE HEADERS. GO BACK AND CHECK LATER IF WE NEED ANY HEADERS
        # IN THE PROXY SERVER FOR ANY REASON
        ########################################################################
        while (get_line_from_socket(conn) != ''):
            pass

        # If we did not get a GET command respond with a 501

        print(request_list)
        if (request_list[0] != 'GET'):
            print('Invalid type of request received ... responding with error!')
            send_response_to_client(conn,'501','501.html')
        
        # If we get the incorrect http version respond with a 505

        elif(request_list[2] != 'HTTP/1.1'):
            print('Invalid HTTP version received ... responding with error!')
            send_response_to_client(conn, '505','505.html')
        
        # We have the correct HTTP version and request type
        
        else:
            
            # Remove the leading / if it exists

            req_file = request_list[1]
            while (req_file[0] == '/'):
                req_file = req_file[1:]
            directory = server[0]+"_"+server[2]+"/"+req_file.rpartition('/')[0]

            # If the directory does not exist, create it and retrieve file
            
            if(os.path.isdir(directory) != True):
            
                
                # Connect to main server

                print("Connecting to proxy server ...")
                try:
                    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    client_socket.connect((server[0], server[2]))
                except ConnectionRefusedError:
                    print("Error: That host or port is not acception connection. Try again later.")
                    sys.exit(1)



                print("Connection to main server established. Sending message ...\n")
                message = prepare_get_message(request, server_info)
                client_socket.send(message.encode())




                # DO THIS WHEN YOU RECEIVE THE FILE BACK AND IT IS NOT A 404
                # For each directory that does not exist in the path to the file, make one

                directoryArray = directory.split('/')
                temp = '.'
                for folder in directoryArray:
                    if(os.path.isdir(temp)):
                        temp = temp + '/' + folder
                    else:
                        os.mkdir(temp)
                        temp = temp + '/' + folder
                os.mkdir(temp) # This is just for the last folder that wasn't added in the for loop

            
            


            

if __name__ == '__main__':
    main()