import sys
import re
import argparse
from urllib.parse import urlparse

def main():
    try:
        if((len(sys.argv) == 4) & (sys.argv[1] == "-proxy")):
            proxyURL = sys.argv[2].partition(':')
            proxyHost = proxyURL[0]
            proxyPort = proxyURL[2]
            if(sys.argv[3].partition(':')[0] != "http"):
                raise ValueError
            serverHost = sys.argv[3].partition('//')[2].partition(':')[0]
            serverPort = sys.argv[3].partition('//')[2].partition(':')[2].partition('/')[0]
            filePath = sys.argv[3].partition('//')[2].partition(':')[2].partition('/')[2]
            fileType = filePath.rpartition(".")[2]
            print(proxyHost)
            print(proxyPort)
            print(serverScheme)
            print(serverHost)
            print(serverPort)
            print(filePath)
            print(fileType)
        elif((len(sys.argv) == 2)):
            parser = argparse.ArgumentParser()
            parser.add_argument("url", help="URL to fetch with an HTTP GET request")
            args = parser.parse_args()
            parsed_url = urlparse(args.url)
            if ((parsed_url.scheme != 'http') or (parsed_url.port == None) or (parsed_url.path == '') or (parsed_url.path == '/') or (parsed_url.hostname == None)):
                raise ValueError
            serverHost = parsed_url.hostname
            serverPort = parsed_url.port
            filePath = parsed_url.path
            fileType = filePath.rpartition(".")[2]
            print(serverHost)
            print(serverPort)
            print(filePath)
            print(fileType)
        else:
            raise ValueError
    except ValueError:
        print('Error:  Invalid Arguments.  Enter a URL of the form:  python3 client.py -proxy proxy_host_here:proxy_port_here http://server_host_here:server_port_here/the/file/path.filetype')
        sys.exit(1)

if __name__ == "__main__":
    main()