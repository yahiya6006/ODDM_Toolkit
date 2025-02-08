from PySide6.QtCore import QSize, QRect, QCoreApplication, QMetaObject, QTimer, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QWidget
from pathlib import Path

# Get the absolute path of the current file (the script inside 'ui' folder)
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Moves 3 levels up to project root
# Construct the path to the assets folder
boot_screen_img = str( BASE_DIR / "assets" / "App_boot_screen.png" )

class boot_window(QWidget):
    boot_complete = Signal()

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setObjectName("boot_screen")
        self.resize(600, 200)
        self.setMinimumSize(QSize(600, 200))
        self.setMaximumSize(QSize(600, 200))

        # Remove title bar (including minimize, maximize, and close buttons)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.label = QLabel(self)
        self.label.setObjectName("label")
        self.label.setGeometry(QRect(0, 0, 600, 200))
        self.label.setMaximumSize(QSize(600, 200))
        self.label.setPixmap(QPixmap(boot_screen_img))

        self.retranslateUi()
        self.show()

        QTimer.singleShot(3000, self.close_boot_screen)

    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("boot_screen", "ODDM Toolkit", None))
        self.label.setText("")

    def close_boot_screen(self):
        self.boot_complete.emit()  # Emit signal before closing
        self.close()