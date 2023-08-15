import sys
from PyQt5.QtWidgets import *

from main import MainWidget

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MainWidget()
    widget.show()
    sys.exit(app.exec_())
