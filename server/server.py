import socket
import os
import datetime
import signal
import sys

# Constant for our buffer size
 
BUFFER_SIZE = 1024
PORT = 9091

# Signal handler for graceful exiting.

def signal_handler(sig, frame):
    print('Interrupt received, shutting down ...')
    sys.exit(0)

# Create an HTTP response

def prepare_response_message(value):
    date = datetime.datetime.now()
    date_string = 'Date: ' + date.strftime('%A, %D %B %Y %H:%M:%S EDT')
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

# Send the given response and file back to the client.

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

    header = prepare_response_message(code) + 'Content-Type: ' + type + '\r\nContent-Length: ' + str(file_size) + '\r\n\r\n\r\n'
    print(header)
    sock.send(header.encode())

    # Open the file, read it, and send it

    with open(file_name, 'rb') as file_to_send:
        while True:
            chunk = file_to_send.read(BUFFER_SIZE)
            if chunk:
                sock.send(chunk)
            else:
                break

# Read a single line (ending with \n) from a socket and return it.
# We will strip out the \r and the \n in the process.

def get_line_from_socket(sock):

    done = False
    line = ''
    while (not done):
        char = sock.recv(1).decode()
        if (char == '\r'):
            pass
        elif (char == '\n'):
            done = True
        else:
            line = line + char
    return line

# Our main function.

def main():

    # Register our signal handler for shutting down.

    signal.signal(signal.SIGINT, signal_handler)

    # Create the socket.  We will ask this to work on any interface and to pick
    # a free port at random.  We'll print this out for clients to use.

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(('', PORT))
    print('Will wait for client connections at port ' + str(client_socket.getsockname()[1]))
    client_socket.listen(1)
    
    # Keep the server running forever.
    
    while(1):
        print('Waiting for incoming client connection ...')
        conn, addr = client_socket.accept()
        print('Accepted connection from client address:', addr)
        print('Connection to client established, waiting to receive message...')

        # We obtain our request from the socket.  We look at the request and
        # figure out what to do based on the headers received
        
        request = get_line_from_socket(conn)
        print(request)
        host_port = get_line_from_socket(conn)
        print(host_port)
        conditional = get_line_from_socket(conn)
        print(conditional)
        request_list = request.split()
        print(request_list)

        # This server doesn't care about headers, so we just clean them up.
        if(conditional != ''):
            while (get_line_from_socket(conn) != ''):
                pass

        # If we did not get a GET command respond with a 501.

        if request_list[0] != 'GET':
            print('Invalid type of request received ... responding with error!')
            send_response_to_client(conn, '501', '501.html')

        # If we did not get the proper HTTP version respond with a 505.

        elif request_list[2] != 'HTTP/1.1':
            print('Invalid HTTP version received ... responding with error!')
            send_response_to_client(conn, '505', '505.html')

        # We have the right request and version, so check if file exists.
                  
        else:

            # If requested file begins with a / we strip it off.

            req_file = request_list[1]
            while (req_file[0] == '/'):
                req_file = req_file[1:]


            # If this is a conditional get

            if(conditional != ''):
                #########################
                # CODE FOR CONDITIONAL GET
                #
                # Return a 304 if the file was not updated, otherwise return file
                #
                #########################
                print('write code here for the conditional GET')

            # If this is a regular get

            else:

                # Check if requested file exists and report a 404 if not.

                if (not os.path.exists(req_file)):
                    print('Requested file does not exist ... responding with error!')
                    send_response_to_client(conn, '404', '404.html')

                # File exists, so prepare to send it!  

                else:
                    print('Requested file good to go!  Sending file ...')
                    send_response_to_client(conn, '200', req_file)
                    
                # We are all done with this client, so close the connection and
                # Go back to get another one!

        conn.close();
    

if __name__ == '__main__':
    main()

