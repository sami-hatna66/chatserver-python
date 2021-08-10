import socket
from _thread import *
import threading
import os
import math
import time

# 2010462373114367427710031420280926994398 = Client disconnected
# 5225735416403254703757706248547980413931 = Sending image file size

ConnectionList = []

def ServerThread(Connection):
    Named = False
    Running = True
    Counter = 0
    Size = 0
    Extension = ""
    BinaryData = b""
    while Running:
        if not Named:
            Data = Connection.recv(1024).decode("UTF-8")
            if Data:
                Named = True
                for conn in ConnectionList:
                    if conn[0] == Connection:
                        conn.append(Data)
                        for connection in ConnectionList:
                            try:
                                connection[0].sendall(("<font color=#008000>--> </font><font color=" + conn[1] + ">" +
                                                       Data  + "</font><font color=#008000> joined the server</font>").encode("UTF-8"))
                            except:
                                pass
                        break
        else:
            for conn in ConnectionList:
                try:
                    conn[0].send(b" ")
                except socket.error:
                    ConnectionList.remove(conn)
                    conn[0].close()
            Data = Connection.recv(40960000)
            Image = False
            try:
                Data = Data.decode("UTF-8")
            except:
                Image = True
            if not Image:
                print("Not Image")
                Tag = "User"
                TagColour = "#0000FF"
                for conn in ConnectionList:
                    if conn[0] == Connection:
                        Tag = str(conn[2])
                        TagColour = str(conn[1])
                if Data == "2010462373114367427710031420280926994398":
                    for conn in ConnectionList:
                        try:
                            conn[0].sendall(("<font color=#008000>--> </font><font color=" + TagColour + ">" +
                                                Tag + "</font><font color=#008000> left the server</font>").encode("UTF-8"))
                        except:
                            pass
                elif Data[0:40] == "5225735416403254703757706248547980413931":
                    Counter = 0
                    Size = int(Data.split()[1])
                    Extension = Data.split()[2]
                    BinaryData = b""
                else:
                    if Data != b"":
                        Message = "<font color=" + TagColour + ">" + Tag + ": </font><font color=black>" + Data+ "</font>"
                        for connection in ConnectionList:
                            try:
                                connection[0].sendall(Message.encode("UTF-8"))
                            except:
                                pass
            else:
                BinaryData += Data
                time.sleep(0.1)
                if len(BinaryData) >= Size:
                    for connection in ConnectionList:
                        connection[0].sendall(bytes("2996054204004259519099311481072272023961 " + str(Size), "UTF-8"))
                        for x in range(0, math.ceil(Size/500000)):
                            Temp = BinaryData[x*500000:(x+1)*500000]
                            connection[0].sendall(Temp)
                    BinaryData = b""
                    Counter = 0
                    Size = 0
                else:
                    Counter += 1




def Main():
    Host = ""
    Port = 65001
    Colours = ["#0000FF", "#FF0000", "#FF00FF", "#6600FF", "#FF6600"]
    ColourPointer = 0

    Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    Socket.bind((Host, Port))
    Socket.listen(5)

    while True:
        Connection, Address = Socket.accept()

        print("Connected to: " + str(Address[0]) + " : " + str(Address[1]))

        ConnectionList.append([Connection, Colours[ColourPointer]])

        if ColourPointer < len(Colours) - 1:
            ColourPointer += 1
        else:
            ColourPointer = 0

        start_new_thread(ServerThread, (Connection,))

if __name__ == "__main__":
    Main()



