from operator import itemgetter             # for sorting a list of tuples
from socket import *
import csv


serverPort = 9000                           # initiate port #9000
serverSocket = socket(AF_INET, SOCK_STREAM) # AF_INET->ipv4, SOCK_STREAM->TCP
serverSocket.bind(('', serverPort))         # bind python with actual socket
serverSocket.listen(1)                      # wait
print('The server is ready to receive')

phones = []                                 # list for phone names and prices
ERRORFLAG=0                                 # used for error detection


# opening phones file and reading phone names and prices_______________________________________________
def openAndParseFile():
    phones.clear()                                                  # empty list of phones
    try:
        with open("phones") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')        # csv file with ',' delimiter
            for row in csv_reader:
                phones.append((row[0], float(row[1])))              # save info as tuples of (name, price)
    except (IOError, FileNotFoundError):
        print('I/O exception')
        global ERRORFLAG
        ERRORFLAG=1                                                 # if theres an error -> flag = 1


# send http file through TCP connection_______________________________________________________________
def sendFile():
    connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())           # file was found
    connectionSocket.send("Content-Type: text/html \r\n".encode())  # file of type html
    connectionSocket.send("\r\n".encode())                          # end header

    # send html file containing the phones and prices
    f1 = open("before", "rt")                                       # html before table
    f3 = open("after", "rt")                                        # html after table
    connectionSocket.send(f1.read().encode())

    for row in phones:                                              # send tuples of (name, price) one by one
        connectionSocket.send(f"<tr> <td>{row[0]}</td> <td>{row[1]}</td></tr>".encode())

    connectionSocket.send(f3.read().encode())


# send http error page through TCP connection______________________________________________________________
def sendErrorPage(addr):
    connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())    # Error
    connectionSocket.send("Content-Type: text/html \r\n".encode())  # html file
    connectionSocket.send("\r\n".encode())                          # end header

    f = open("error", "rt")
    connectionSocket.send(f.read().encode())
    connectionSocket.send(f"<br><br>IP: {addr[0]} <br> port: {addr[1]} ".encode())  # client IP and Port
    connectionSocket.send("</body> </html>".encode())


# send http/css/png/jpg file through TCP connection________________________________________________________
def sendPage(fileType, addr):
    try:
        file = open(fileType, "rb")                                # open the file in binary format for reading
    except (IOError, FileNotFoundError):                           # if file could not be opened
        print('I/O exception2')
        sendErrorPage(addr)
    else:
        dotLocation = fileType.index('.')
        extension = fileType[dotLocation+1:]
        connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())    # # indicates that the request has succeeded
        if extension == "html":
            connectionSocket.send("Content-Type: text/html \r\n".encode())  # html file
        elif extension == "css":
            connectionSocket.send("Content-Type: text/css \r\n".encode())   # css file
        elif extension == "jpg":
            connectionSocket.send("Content-Type: image/jpg \r\n".encode())  # jpg file
        else:
            connectionSocket.send("Content-Type: image/png \r\n".encode())  # png file

        connectionSocket.send("\r\n".encode())
        content = file.read()                                               # read the file
        connectionSocket.send(content)                                      # send file


while True:
    # accept three way handshake
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024).decode()
    print(sentence)

    # extracting request type from request
    headers = sentence.split('\n')
    filename = headers[0].split()[1]  # The second bit of the first bit of the headers contains the request
    reqType = filename.lstrip('/')  # remove the / on the left of the string

    # carry out the request
    if reqType.lower() == "sortname":  # __________________________________________________________
        openAndParseFile()
        if ERRORFLAG == 1:                              # if an error was found in the function ->
            ERRORFLAG=0
            sendErrorPage(addr)                         # send error html page
        else:
            phones = sorted(phones, key=itemgetter(0))  # sort by name
            sendFile()

    elif reqType.lower() == "sortprice":  # _______________________________________________________
        openAndParseFile()
        if ERRORFLAG == 1:                              # if an error was found in the function ->
            ERRORFLAG = 0
            sendErrorPage(addr)                         # send error html page
        else:
            phones = sorted(phones, key=itemgetter(1))  # sort by price
            sendFile()

    elif reqType.lower() == "":  # ____________________________________________________
        sendPage("index.html", addr)

    elif reqType.lower().__contains__(".png"):  # __________________________________________________
        sendPage(reqType, addr)

    elif reqType.lower().__contains__(".jpg"):  # __________________________________________________
        sendPage(reqType, addr)

    elif reqType.lower().__contains__(".css"):  # __________________________________________________
        sendPage(reqType, addr)

    elif reqType.lower().__contains__(".html"):  # __________________________________________________
        sendPage(reqType, addr)
    else:  # ________________________________________________________________________________________
        sendErrorPage(addr)


    #close TCP connection
    connectionSocket.close()