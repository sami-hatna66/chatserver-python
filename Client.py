import socket
from _thread import *
import threading
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import time
import math
import os

# 2010462373114367427710031420280926994398 = Client disconnected
# 5225735416403254703757706248547980413931 = Sending image file size
# 2996054204004259519099311481072272023961 = Server sending image file

class ReceiveThread(QThread):
    NewTextSignal = pyqtSignal(str)
    NewImageSignal = pyqtSignal(bytes)
    def __init__(self, Socket):
        super(ReceiveThread, self).__init__()
        self.Socket = Socket
        self.Running = True

    def run(self):
        while self.Running:
            try:
                Data = self.Socket.recv(40960000)
                if Data.decode("UTF-8").strip().split()[0] == "2996054204004259519099311481072272023961":
                    Size = int(Data.decode("UTF-8").strip().split()[1])
                    RecvImageData = b""
                    while len(RecvImageData) < Size:
                        ImagePart = self.Socket.recv(40960000)
                        RecvImageData += ImagePart
                        time.sleep(0.1)
                    self.NewImageSignal.emit(RecvImageData)
                else:
                    self.NewTextSignal.emit(Data.decode("UTF-8"))
                time.sleep(0.5)
            except:
                pass

    def stop(self):
        self.Running = False
        self.Socket.close()
        self.quit()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        Host = "192.168.0.32"
        Port = 65001

        self.MessageWidgetInstances = []
        self.Named = False

        self.setMinimumSize(300, 400)

        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.Socket.connect((Host, Port))

        self.Worker = ReceiveThread(Socket=self.Socket)
        self.Worker.NewTextSignal.connect(self.NewTextSlot)
        self.Worker.NewImageSignal.connect(self.NewImageSlot)
        self.Worker.start()

        self.CentralWidget = QWidget()
        self.setCentralWidget(self.CentralWidget)

        self.Layout = QVBoxLayout()
        self.CentralWidget.setLayout(self.Layout)

        self.ChatScroll = QScrollArea()
        self.ChatScroll.setWidgetResizable(True)
        self.ChatWidget = QWidget()
        self.ChatWidget.setStyleSheet("background-color: white")
        self.ChatLayout = QVBoxLayout()
        self.ChatLayout.setSpacing(5)
        self.ChatLayout.setContentsMargins(5,5,5,5)
        self.ChatLayout.setAlignment(Qt.AlignTop)
        self.ChatWidget.setLayout(self.ChatLayout)
        self.ChatScroll.setWidget(self.ChatWidget)
        self.Layout.addWidget(self.ChatScroll)

        VBar = self.ChatScroll.verticalScrollBar()
        VBar.rangeChanged.connect(lambda x,y: VBar.setValue(y))

        self.HBL = QHBoxLayout()
        self.Layout.addLayout(self.HBL)

        self.InputBox = QLineEdit()
        self.InputBox.setPlaceholderText("Input Username")
        self.HBL.addWidget(self.InputBox)

        self.SendBTN = QPushButton("Submit")
        self.SendBTN.clicked.connect(self.SubmitName)
        self.HBL.addWidget(self.SendBTN)

        self.ImageBTN = QPushButton("Img")
        self.ImageBTN.clicked.connect(self.SendImage)
        self.HBL.addWidget(self.ImageBTN)
        self.ImageBTN.hide()

        self.show()

    def SendImage(self):
        self.FileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", os.path.abspath(os.sep),
                                                       "Image files (*.jpg *.png)")
        if self.FileName:
            # Send in chunks of 100,000 bytes
            Data = open(self.FileName, "rb")
            Size = os.path.getsize(self.FileName)
            self.Socket.sendall(bytes("5225735416403254703757706248547980413931 " + str(Size) + " " + os.path.splitext(self.FileName)[1], "UTF-8"))
            while True:
                ReadBytes = Data.read(500000)
                if not ReadBytes:
                    break
                self.Socket.sendall(ReadBytes)

    def SubmitName(self):
        if self.InputBox.text() != "":
            self.Socket.sendall(self.InputBox.text().encode("UTF-8"))
            self.InputBox.setText("")
            self.InputBox.setPlaceholderText("")
            self.SendBTN.setText("Send")
            self.SendBTN.clicked.disconnect()
            self.SendBTN.clicked.connect(self.SendMessage)
            self.Named = True
            self.ImageBTN.show()

    def keyPressEvent(self, QKeyEvent):
        if QKeyEvent.key() == Qt.Key_Enter or QKeyEvent.key() == Qt.Key_Return:
            if not self.Named:
                self.SubmitName()
            else:
                self.SendMessage()

    def NewTextSlot(self, Text):
        if Text != " " and not (Text.isspace()):
            Temp = MessageWidget(Text=Text)
            self.ChatLayout.addWidget(Temp)
            self.MessageWidgetInstances.append(Temp)

    def NewImageSlot(self, BinaryData):
        Temp = ImageWidget(BinaryData=BinaryData)
        self.ChatLayout.addWidget(Temp)
        self.MessageWidgetInstances.append(Temp)

    def SendMessage(self):
        self.Socket.sendall(self.InputBox.text().encode("UTF-8"))
        self.InputBox.setText("")

    def closeEvent(self, event):
        self.Socket.sendall(str(2010462373114367427710031420280926994398).encode("UTF-8"))
        self.Worker.stop()
        self.Socket.close()

class MessageWidget(QWidget):
    def __init__(self, Text):
        super(MessageWidget, self).__init__()
        self.setStyleSheet("border-bottom: 1px solid #d3d3d3; padding-bottom: 5px")
        self.Layout = QVBoxLayout()
        self.Layout.setContentsMargins(0,0,0,0)
        self.LBL = QLabel(Text)
        self.Layout.addWidget(self.LBL)
        self.setLayout(self.Layout)
        self.show()

class ImageWidget(QWidget):
    def __init__(self, BinaryData):
        super(ImageWidget, self).__init__()
        self.setStyleSheet("border-bottom: 1px solid #d3d3d3; padding-bottom: 5px")
        self.Layout = QVBoxLayout()
        self.Layout.setContentsMargins(0,0,0,0)

        self.BinaryData = BinaryData

        Image = QImage.fromData(self.BinaryData)
        Pixmap = QPixmap.fromImage(Image)
        Pixmap = Pixmap.scaledToWidth(200, Qt.SmoothTransformation)
        self.PixmapLBL = QLabel()
        if Pixmap.isNull():
            self.PixmapLBL.setText("<font color=#008000>--><font color=#FF0000> Error</font><font color=#008000> Sending Image</font>")
        else:
            self.PixmapLBL.setPixmap(Pixmap)
        self.Layout.addWidget(self.PixmapLBL)

        self.setLayout(self.Layout)
        self.show()

    def mousePressEvent(self, QMouseEvent):
        self.OpenImage = ImageWindow(BinaryData=self.BinaryData)

class ImageWindow(QWidget):
    def __init__(self, BinaryData):
        super(ImageWindow, self).__init__()
        Image = QImage.fromData(BinaryData)
        self.Pixmap = QPixmap.fromImage(Image)
        self.resize(QSize(self.Pixmap.width(), self.Pixmap.height()))
        self.show()

    def  paintEvent(self, QPainEvent):
        Painter = QPainter()
        Painter.begin(self)

        Painter.drawPixmap(self.rect(), self.Pixmap)

        Painter.end()



if __name__ == "__main__":
    App = QApplication(sys.argv)
    Root = MainWindow()
    sys.exit(App.exec())
