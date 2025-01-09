import datetime
import time

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox, QWidget

from keysight import KS34460A
from ui_widget import Ui_Widget


ks34460a = KS34460A()


class Widget(QWidget, Ui_Widget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("KS34460 Instrument Control")

        # Make the connections
        self.writeButton.clicked.connect(self.write)
        self.queryButton.clicked.connect(self.query)
        self.readButton.clicked.connect(self.read)
        self.exitButton.clicked.connect(self.exit)
        self.cqueryButton.clicked.connect(self.cquery)
        self.wsCheckBox.stateChanged.connect(self.ws)
        self.cbButton.clicked.connect(self.cb)  # clear buffer
        self.commandComboBox.activated.connect(self.ccb)  # commandComboBox
        self.ctcButton.clicked.connect(self.cbcopied)
        self.rsbButton.clicked.connect(self.rsb)
        self.ccButton.clicked.connect(self.cc)
        self.btrSpinBox.valueChanged.connect(self.bsb)
        self.chunk_size = self.btrSpinBox.value()  # byte to read spinbox
        self.stButton.clicked.connect(self.settime)  # set time
        self.viewComboBox.currentIndexChanged.connect(self.viewcb)

    def query(self):
        response = self.readTextEdit.toPlainText()
        response = (
            response
            + ts()
            + "Q: "
            + self.commandTextEdit.toPlainText()
            + "; A: "
            + ks34460a.inst.query(self.commandTextEdit.toPlainText())
        )
        self.ende(response)

    def syserror(self, response):
        return response + ts() + "System Error: " + ks34460a.inst.query("SYSTem:ERRor?")

    def ende(self, response):
        response = self.syserror(response)
        self.readTextEdit.setText(response)
        self.readTextEdit.moveCursor(QtGui.QTextCursor.End)

    def cquery(self):
        response = self.readTextEdit.toPlainText()
        loop = self.flnSpinBox.value()
        for _ in range(loop):
            response = (
                response
                + ts()
                + "Q: "
                + self.commandTextEdit.toPlainText()
                + "; A: "
                + ks34460a.inst.query(self.commandTextEdit.toPlainText())
            )
            self.ende(response)
            QApplication.processEvents()  # Allow UI to update
            time.sleep(self.stDoubleSpinBox.value())

    def ws(self, state):
        if state == 2:  # Checked
            self.run_whileloop()

    def run_whileloop(self):
        response = self.readTextEdit.toPlainText()
        while self.wsCheckBox.isChecked():
            # response = response + ts() + "Time: " + timestamp() + "\n"

            response = (
                response
                + ts()
                + "Q: "
                + self.commandTextEdit.toPlainText()
                + "; A: "
                + ks34460a.inst.query(self.commandTextEdit.toPlainText())
            )
            self.ende(response)
            QApplication.processEvents()  # Allow UI to update
            time.sleep(self.stDoubleSpinBox.value())

    def write(self):
        response = self.readTextEdit.toPlainText()
        response = (
            response
            + ts()
            + "Write: "
            + self.commandTextEdit.toPlainText()
            + "; Bytes: "
            + str(ks34460a.inst.write(self.commandTextEdit.toPlainText()))
            + "\n"
        )
        self.readTextEdit.setText(response)
        self.readTextEdit.moveCursor(QtGui.QTextCursor.End)

    def read(self):
        response = self.readTextEdit.toPlainText()
        res = str(ks34460a.inst.read()).rstrip()
        response = response + ts() + "Read: " + res + "; Bytes: " + str(len(res)) + "\n"
        self.ende(response)

    def cb(self):
        self.readTextEdit.setText("")

    def cc(self):
        self.commandTextEdit.setText("")

    def ccb(self):
        self.commandTextEdit.setText(self.commandComboBox.currentText())

    def rsb(self):
        response = self.readTextEdit.toPlainText()
        response = response + ts() + "Q: *STB?; A: " + ks34460a.inst.query("*STB?")
        self.ende(response)

    def bsb(self):
        chunk_size = self.btrSpinBox.value()
        print("chunk size: " + str(chunk_size))
        return chunk_size

    def log(self):
        # Create text file for saving log
        fn = r"C:\TestData\Python\Keysight34460A\KS34460A_Log_" + timestamp2() + ".txt"

        with open(fn, "x") as f:
            f.write(self.cbcopied())

    def cbcopied(self):
        clipboard = QApplication.clipboard()
        cb = self.readTextEdit.toPlainText()
        clipboard.setText(cb)
        return cb
        # print(cb)

    def settime(self):
        now = datetime.datetime.now()
        # year = now.strftime("+%Y,") + now.strftime("+%m,") + now.strftime("+%d")
        hour = now.strftime("%H,") + now.strftime("%M,") + str(float(now.strftime("%S")) + 1)
        # ks34460a.inst.write("SYSTem:DATE " + year)
        # print(now.strftime("%f"))
        time.sleep(0.999 - float(now.strftime("%f"))/1000000)
        ks34460a.inst.write("SYSTem:TIME " + hour)

    def viewcb(self, index):
        if index == 1:
            text = self.readTextEdit.toPlainText()
            hex_output = ascii_to_hex(text)
            self.readTextEdit.setText(hex_output)
        elif index == 0:
            hex_string = self.readTextEdit.toPlainText()
            print(hex_string)
            ascii_string = hex_to_ascii(hex_string)
            self.readTextEdit.setText(ascii_string)

    def exit(self):
        ks34460a.close()
        self.log()
        self.close()


def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")


def timestamp2():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def ts():
    return timestamp() + ": "


def ascii_to_hex(asci):
    return " ".join(hex(ord(c))[2:] for c in asci)


def hex_to_ascii(hexy):
    hexy = hexy.replace(" a", " 0a")
    hexz = "".join(hexy.split())
    return bytes.fromhex(hexz).decode("ascii")
