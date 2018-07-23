from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
class MainForm(QDialog):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)
        self.child = None
        self.table = QTableWidget()
        self.table.setColumnCount(40)
        self.table.setRowCount(30)
        # set Column tab title
        #self.table.setHorizontalHeaderLabels(list(range(5,10)))
        for i in range(0, 5):
            for x in range(0, 7):
                item = QTableWidgetItem(str(i + x))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignCenter)
                item.setBackgroundColor(Qt.green)
                self.table.setItem(x, i, item)

        lbutton = QPushButton("&L")
        Vlayout = QHBoxLayout()
        Vlayout.addWidget(lbutton)
        Hlayout = QVBoxLayout()
        Hlayout.addWidget(self.table)
        Hlayout.addLayout(Vlayout)
        self.setLayout(Hlayout)
        self.resize(400,300)
        self.setWindowTitle("Table")
        self.connect(lbutton, SIGNAL("clicked()"), self.liveChange)

    def callback(self, c=0, r=0):
        print('c=' + str(c) + 'r=' + str(r))
        self.table.clear()
        for i in range(0, c):
            for x in range(0, r):
                item = QTableWidgetItem(str(i + x))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignCenter)
                item.setBackgroundColor(Qt.red)
                self.table.setItem(x, i, item)

    def liveChange(self):
        if self.child == None:
            self.child = liveDialog(self.callback, self)
        self.child.show()
        self.child.raise_()
        self.child.activateWindow()


class liveDialog(QDialog):
    def __init__(self, callback, parent=None):
        super(liveDialog, self).__init__(parent)
        self.callback = callback
        self.c_edit = QLineEdit()
        self.r_edit = QLineEdit()
        layout = QHBoxLayout()
        layout.addWidget(self.c_edit)
        layout.addWidget(self.r_edit)
        self.setLayout(layout)
        self.connect(self.c_edit, SIGNAL("textChanged(QString)"), self.updateUi)
        self.connect(self.r_edit, SIGNAL("textEdited(QString)"), self.updateUi)

    def updateUi(self, text):
        c = self.c_edit.text()
        r = self.r_edit.text()
        if c and r:
            self.callback(int(c), int(r))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mf = MainForm()
    mf.show()
    app.exec_()