import socket
import os
import datetime
import signal
import sys

PORT = 8082
BUFFER_SIZE = 1024 # bytes
EXPIRY = 30 # Second

# Signal handler for graceful exiting.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)

def prepare_get_message(line1, line2):
    request = line1 + '\r\n'+  line2 + '\r\n\r\n'
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

# Create an HTTP response

def prepare_response_message(value):
    date = datetime.datetime.now()
    date_string = 'Date: ' + date.strftime('%a, %d %b %Y %H:%M:%S EDT')
    message = 'HTTP/1.1 '
    if value == '200':
        message = message + value + ' OK\r\n' + date_string + '\r\n'
    elif value == '404':
        message = message + value + ' Not Found\r\n' + date_string + '\r\n'
    elif value == '501':
        message = message + value + ' Method Not Implemented\r\n' + date_string + '\r\n'
    elif value == '505':
        message = message + value + ' Version Not Supported\r\n' + date_string + '\r\n'
    return message

def send_response_to_client(sock, code, file_name):
    # Determine content type of file

    if ((file_name.endswith('.jpg')) or (file_name.endswith('.jpeg'))):
        type = 'image/jpeg'
    elif (file_name.endswith('.gif')):
        type = 'image/gif'
    elif (file_name.endswith('.png')):
        type = 'image/jpegpng'
    elif ((file_name.endswith('.html')) or (file_name.endswith('.htm'))):
        type = 'text/html'
    else:
        type = 'application/octet-stream'
    
    # Get size of file

    file_size = os.path.getsize(file_name)

    # Construct header and send it

    header = prepare_response_message(code) + 'Content-Type: ' + type + '\r\nContent-Length: ' + str(file_size) + '\r\n\r\n'
    sock.send(header.encode())

    # Open the file, read it, and send it

    with open(file_name, 'rb') as file_to_send:
        while True:
            chunk = file_to_send.read(BUFFER_SIZE)
            if chunk:
                sock.send(chunk)
            else:
                break

# Forward error responses

def forward_response_to_client(resp, client, server):
    
    # Get all the headers so that we can get the error file

    response = resp
    date = get_line_from_socket(server)
    content_type = get_line_from_socket(server)
    content_length = get_line_from_socket(server)
    # Remove any remining headers and forward headers to client

    while(get_line_from_socket(server) != ''):
        pass
    client_response = response + '\r\n' + date + '\r\n' + content_type + '\r\n' + content_length + '\r\n'
    print(client_response)
    client.send(client_response.encode())
    print('SENT HEADER')
    # Forward file to client
    print('Now sending file')
    length = content_length.split(' ')
    bytes_to_send = int(length[1])
    bytes_sent = 0
    while(bytes_sent < bytes_to_send):
        chunk = server.recv(BUFFER_SIZE)
        bytes_sent += len(chunk)
        client.send(chunk)

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

            # If the directory does not exist, retrieve file if it exists and create directory
            
            if(os.path.isdir(directory) != True):
            
                # Connect to main server

                print("Connecting to main server ...")
                try:
                    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    server_socket.connect((server[0], int(server[2])))
                except ConnectionRefusedError:
                    print("Error: That host or port is not acception connection. Try again later.")
                    sys.exit(1)



                print("Connection to main server established. Sending message ...\n")
                message = prepare_get_message(request, server_info)
                print(message)
                server_socket.send(message.encode())

                response_line = get_line_from_socket(server_socket)
                print(response_line)
                response_list = response_line.split(' ')

                # If file does not exist, or error is encountered
                
                if response_list[1] != '200':
                    print('going to forward response to client method')
                    forward_response_to_client(response_line, conn, server_socket)
                
                # File exists

                else:
                    
                    print('Success:  Server is sending file.  Downloading it now.')
                    
                    # Create the directory for this file

                    directoryArray = directory.split('/')
                    temp = '.'
                    for folder in directoryArray:
                        if(os.path.isdir(temp)):
                            temp = temp + '/' + folder
                        else:
                            os.mkdir(temp)
                            temp = temp + '/' + folder
                    os.mkdir(temp) # This is just for the last folder that wasn't added in the for loop


        
        
        conn.close()
            
            


            

if __name__ == '__main__':
    main()