##======================================================================================##
##  DESCRIPTION                                                                         ##
##======================================================================================##
#
#   Program to decipher morse code.
#   Version: 0.2.0
#
##======================================================================================##
##  IMPORTS                                                                             ##
##======================================================================================##

import sys
import random
from pprint import pprint
from mc_dict import mc_dict
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from functools import partial

##======================================================================================##
##  CLASS DEFINITIONS                                                                   ##
##======================================================================================##

class main_window(QtGui.QMainWindow):

    #Initialize main window
    def __init__(self):
        super(main_window, self).__init__()
        self.init()

    #Populate main window
    def init(self):
        QtGui.QMainWindow.__init__(self)
        self.setGeometry(500, 200, 500, 500)
        self.setWindowTitle('Main Window')

        appbtn = QtGui.QPushButton('App', self)
        appbtn.clicked.connect(self.enter_mc)
        appbtn.resize(250, 500)

        gamebtn = QtGui.QPushButton('Game', self)
        gamebtn.clicked.connect(self.enter_game)
        gamebtn.resize(250, 500)
        gamebtn.move(250, 0)

    #Activate application window
    def enter_mc(self):
        global window
        window = morse_code()
        window.show()

    #Activate game window
    def enter_game(self): 
        global play
        play = mc_play(mc_dict)
        play.show()

class timer_thread(QtCore.QThread):

    #Initialize thread
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.alive = 1
        self.running = 0

    #Run timer thread
    def run(self):
        while self.alive:
            while self.running:
                self.emit(QtCore.SIGNAL("dosomething(QString)"), str(self.time))
                self.msleep(1000)
                self.time -= 1
                if not self.time:
                    self.emit(QtCore.SIGNAL("dosomething(QString)"), str("End"))
                    self.running = 0

    #Turn timer thread on/off
    def toggle(self):
        if self.running:
            self.running = 0
        else:
            self.running = 1
            self.time = 5

    #End timer thread
    def stop(self):
        self.alive = 0

class mc_play(QtGui.QWidget):

    #Initialize and populate game window
    def __init__(self, mapping):
        QtGui.QWidget.__init__(self)
        grid = QtGui.QGridLayout()
        self.buttons = []
        i = 0
        j = 0

        self.timer = timer_thread()
        self.timer.start()

        self.start_btn = QtGui.QPushButton('Start', self)
        self.start_btn.clicked.connect(self.generate_mc)
        grid.addWidget(self.start_btn, 0, 0)

        self.connect(self.start_btn, QtCore.SIGNAL("clicked()"), self.timer.toggle)
        self.connect(self.timer, QtCore.SIGNAL("dosomething(QString)"), self.out_thread)

        self.quest = QtGui.QLabel(self)
        self.quest.setText('Press Start')
        grid.addWidget(self.quest, 0, 1)

        self.te = QtGui.QTextEdit(self)
        self.te.setMaximumHeight(25)
        grid.addWidget(self.te, 0, 2, 1, 3)

        self.status = QtGui.QLabel(self)
        self.status.setText('Waiting...')
        grid.addWidget(self.status, 0,5)

        self.time_left = QtGui.QLabel(self)
        self.time_left.setText('Time')
        grid.addWidget(self.time_left, 0, 6)

        self.answer = QtGui.QLabel(self)
        self.answer.setText('Answer')
        grid.addWidget(self.answer, 0, 7)

        i += 1
        for key, value in mc_dict.iteritems():
            self.buttons.append(QtGui.QPushButton(key,self))
            self.buttons[-1].clicked.connect(partial(self.output, data=value))
            grid.addWidget(self.buttons[-1], i, j)
            if i < 7:
                i += 1
            else:
                i = 1
                j += 1
        self.setLayout(grid)

    #Interact with timer thread
    def out_thread(self, text):
        self.time_left.setText(text)
        test = self.time_left.text()
        if test == "End":
            self.time_left.setText('Time')
            self.start_btn.setText('Start')
            self.quest.setText('Press Start')
            self.status.setText('Waiting...')
            self.te.setPlainText('')
            self.answer.setText(self.rand_key)

    #Output data
    def output(self, data = "\n"):
        self.te.setPlainText(data)
        test = self.quest.text()
        if test != 'Press Start':
            if data == test:
                self.status.setText('Match')
            else:
                self.status.setText('No Match')

    #Begin game
    def generate_mc(self):
        test = self.start_btn.text()
        if test == 'Start':
            self.start_btn.setText('Stop')
            self.rand_key = random.choice(mc_dict.keys())
            rand_mc = mc_dict[self.rand_key]
            self.quest.setText(rand_mc)
        elif test == 'Stop':
            self.start_btn.setText('Start')
            self.quest.setText('Press Start')
            self.status.setText('Waiting...')

class morse_code(QtGui.QMainWindow):

    #Initialize app window
    def __init__(self):
        super(morse_code, self).__init__()
        self.initUI()

    #Populate app window
    def initUI(self):
        QtGui.QMainWindow.__init__(self)
        self.setGeometry(500, 200, 500, 500)
        self.setWindowTitle('Morse Code Decipher')

        quitbtn = QtGui.QPushButton('Quit', self)
        quitbtn.clicked.connect(QtCore.QCoreApplication.instance().quit)
        quitbtn.setToolTip('Quit Morse Code Decipher')
        quitbtn.resize(quitbtn.sizeHint())
        quitbtn.move(400,470)

        mc_out_btn = QtGui.QPushButton('Output Morse Code', self)
        mc_out_btn.clicked.connect(self.output_mc)
        mc_out_btn.setToolTip('Output Morse Code from English')
        mc_out_btn.resize(mc_out_btn.sizeHint())
        mc_out_btn.move(10,445)

        read_mc_btn = QtGui.QPushButton('Decipher Morse Code', self)
        read_mc_btn.clicked.connect(self.open_mc)
        read_mc_btn.setToolTip('Translate Morse Code to English')
        read_mc_btn.resize(read_mc_btn.sizeHint())
        read_mc_btn.move(10, 470)

        file_mc_out = QtGui.QAction(QtGui.QIcon('open.png'), 'Output Morse Code', self)
        file_mc_out.setStatusTip('Open a file and output Morse Code')
        file_mc_out.triggered.connect(self.output_mc)

        file_read_mc = QtGui.QAction(QtGui.QIcon('open.png'), 'Decipher Morse Code', self)
        file_read_mc.setStatusTip('Open a file and decipher Morse Code')
        file_read_mc.triggered.connect(self.open_mc)

        menubar = self.menuBar()
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(file_mc_out)
        filemenu.addAction(file_read_mc)

        self.btn = QtGui.QPushButton('Save Text', self)
        self.btn.move(10, 25)
        self.btn.clicked.connect(self.save_text)
        self.btn.resize(self.btn.sizeHint())
        self.btn.setToolTip('Save text to a file')

        self.open_btn = QtGui.QPushButton('Open File', self)
        self.open_btn.move(10, 50)
        self.open_btn.clicked.connect(self.open_dlg)
        self.open_btn.resize(self.open_btn.sizeHint())
        self.open_btn.setToolTip('Open a file')

        self.te = QtGui.QTextEdit('This is text', self)
        self.te.resize(375,410)
        self.te.move(100,25)

    #Save text message to file
    def save_text(self):
        text = self.te.toPlainText()
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save File', '.')
        fname = open(filename, 'w')
        fname.write(str(text))
        fname.close()

    #Open text file
    def open_dlg(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '\home')
        f = open(fname, 'r')
        with f:
            data = f.read()
            self.te.setPlainText(data)

    #Convert morse code to text
    def open_mc(self):
        text = self.te.toPlainText()
        msg = text_message(text)
        self.te.setPlainText(msg)

    #Convert text to morse code
    def output_mc(self):
        text = self.te.toPlainText()
        msg = mc_message(text)
        self.te.setPlainText(msg)

##======================================================================================##
##  FUNCTION DEFINITIONS                                                                ##
##======================================================================================##

#Converts morse code to text
def text_message(message):
    message = str(message)
    match= ''
    temp = ''
    for char in message:
        if char != '\n':
            temp += char
        else:
            for key in mc_dict:
                if temp == mc_dict[key]:
                    if key != '&&':
                        match += key
            temp = ''
    return match

#Converts text to morse code
def mc_message(message):
    message = str(message)
    temp = ''
    for c in message:
        c = c.upper()
        for key in mc_dict:
            if c == key:
                temp += mc_dict[key] + '\n'
    return temp

##=================##
##  MAIN FUNCTION  ##
##=================##

def main():
    app = QtGui.QApplication(sys.argv)
    mc = main_window()
    mc.show()
    sys.exit(app.exec_())

##======================================================================================##
##  MAIN BODY                                                                           ##
##======================================================================================##

if __name__ == '__main__':
    main()
