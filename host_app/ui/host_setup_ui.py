from PySide6.QtCore import Qt, QSize, QRect, QCoreApplication, QMetaObject, Signal
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QSpacerItem, QSizePolicy, QMessageBox, QStackedWidget
from PySide6.QtGui import QColor, QPalette
from .theme import *

# Custom QLineEdit to handle backspace key press
class PasswordLineEdit(QLineEdit):
    enterPressed = Signal()  # Custom signal to trigger submit button

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            self.clear()  # Clear the input field when backspace is pressed
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):  # Check for Enter key
            self.enterPressed.emit()  # Emit the signal when Enter is pressed
        else:
            super().keyPressEvent(event)  # Call the original key event handler

class SetupPasswordWidget(QWidget):
    passwordSubmitted = Signal(str)
    userDetailsSubmitted = Signal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.setupUi()
    
    def setupUi(self):
        self.setObjectName("setup_password")
        self.setFixedSize(400, 250)  # Fixed size for a clean UI

        self.setWindowTitle("ODDM Toolkit - Host Setup")

        # Set background color
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(BACKGROUND_COLOR))  # Apply theme background
        self.setPalette(palette)

        # Create QStackedWidget
        self.stacked_widget = QStackedWidget(self)

        # Create pages
        self.password_page = self.create_db_password_widget()
        self.user_page = self.create_user_page()
        self.stacked_widget.addWidget(self.password_page)
        self.stacked_widget.addWidget(self.user_page)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
        
    def create_db_password_widget(self):
        page = QWidget()
        # Layout
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)  # Add padding around the edges
        layout.setSpacing(15)  # Set spacing between widgets
        
        # Instruction label
        label = QLabel()
        label.setObjectName("instruction_label")
        label.setText("Please enter your PostgreSQL password to kickstart the ODDM Toolkit host setup. We just need it to set things up.")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            color: {TEXT_PRIMARY_COLOR}; 
            font-size: {TEXT_SIZE_HEADING}; 
            font-weight: bold;
            font-family: {TEXT_FONT_FAMILY};
        """)
        layout.addWidget(label)

        # Add vertical space
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Password input
        self.password_input = PasswordLineEdit()
        self.password_input.setObjectName("password_input")
        self.password_input.setPlaceholderText("Enter PostgreSQL password")
        self.password_input.setEchoMode(QLineEdit.Password)  # Hide password input
        self.password_input.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
        """)
        self.password_input.setFixedWidth(250)
        layout.addWidget(self.password_input, alignment=Qt.AlignCenter)
        
        # Submit button
        self.submit_button = QPushButton()
        self.submit_button.setObjectName("submit_button")
        self.submit_button.setText("Submit")
        self.submit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_BUTTON_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        self.submit_button.setFixedSize(80, 28)
        layout.addWidget(self.submit_button, alignment=Qt.AlignCenter)
        
        # self.setLayout(layout)
        # QMetaObject.connectSlotsByName(self)

        self.password_input.enterPressed.connect(self.submit_button.click)

        self.submit_button.clicked.connect(self.submit_psql_password)

        page.setLayout(layout)
        return page
    
    def submit_psql_password(self):
        password = self.password_input.text()
        self.password_input.setReadOnly(True)
        self.submit_button.setEnabled(False)
        self.passwordSubmitted.emit(password)

    def show_error_dialog(self, message):
        """Displays an error message."""
        error_dialog = ErrorDialog(message, self)
        error_dialog.exec_()

        # Re-enable input fields
        self.password_input.setReadOnly(False)
        self.password_input.clear()
        self.submit_button.setEnabled(True)

    def create_user_page(self):
        page = QWidget()
        # Layout
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        # layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel()
        label.setObjectName("setup_user_label")
        label.setText("Setup ODDM Superuser")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            color: {TEXT_PRIMARY_COLOR}; 
            font-size: {TEXT_SIZE_HEADING}; 
            font-weight: bold;
            font-family: {TEXT_FONT_FAMILY};
        """)
        layout.addWidget(label)

        self.oddm_db_password_input = QLineEdit()
        self.oddm_db_password_input.setObjectName("oddm_db_password_input")
        self.oddm_db_password_input.setPlaceholderText("ODDM DB Preferred Password")
        self.oddm_db_password_input.setEchoMode(QLineEdit.Password)  # Hide password input
        self.oddm_db_password_input.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
        """)
        self.oddm_db_password_input.setFixedWidth(250)
        layout.addWidget(self.oddm_db_password_input, alignment=Qt.AlignCenter)

        self.superuser_email_input = QLineEdit()
        self.superuser_email_input.setObjectName("superuser_email_input")
        self.superuser_email_input.setPlaceholderText("Superuser email")
        self.superuser_email_input.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
        """)
        self.superuser_email_input.setFixedWidth(250)
        layout.addWidget(self.superuser_email_input, alignment=Qt.AlignCenter)

        self.superuser_username_input = QLineEdit()
        self.superuser_username_input.setObjectName("superuser_username_input")
        self.superuser_username_input.setPlaceholderText("Superuser Username")
        self.superuser_username_input.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
        """)
        self.superuser_username_input.setFixedWidth(250)
        layout.addWidget(self.superuser_username_input, alignment=Qt.AlignCenter)

        self.superuser_password_input = QLineEdit()
        self.superuser_password_input.setObjectName("superuser_password_input")
        self.superuser_password_input.setPlaceholderText("Superuser Password")
        self.superuser_password_input.setEchoMode(QLineEdit.Password)  # Hide password input
        self.superuser_password_input.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
        """)
        self.superuser_password_input.setFixedWidth(250)
        layout.addWidget(self.superuser_password_input, alignment=Qt.AlignCenter)

        # Submit button
        self.user_submit_button = QPushButton()
        self.user_submit_button.setObjectName("user_submit_button")
        self.user_submit_button.setText("Submit")
        self.user_submit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_BUTTON_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        self.user_submit_button.setFixedSize(80, 28)
        layout.addWidget(self.user_submit_button, alignment=Qt.AlignCenter)
        self.user_submit_button.clicked.connect(self.submit_user_details)

        page.setLayout(layout)
        return page

    def submit_user_details(self):
        oddm_password = self.oddm_db_password_input.text()
        superuser_email = self.superuser_email_input.text()
        superuser_name = self.superuser_username_input.text()
        superuser_password = self.superuser_password_input.text()

        if not oddm_password or not superuser_email or not superuser_name or not superuser_password:
            self.show_error_dialog("All fields are required.")
            return

        self.userDetailsSubmitted.emit(oddm_password, superuser_email, superuser_name, superuser_password)

class ErrorDialog(QMessageBox):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error")
        self.setText(message)
        self.setIcon(QMessageBox.Critical)
        self.setStyleSheet(
            f"""
            QMessageBox {{
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_PRIMARY_COLOR};
            }}
            QPushButton {{
                background-color: {PRIMARY_BUTTON_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 5px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};
            }}
            """
        )

        ok_button = self.addButton("OK", QMessageBox.AcceptRole)
        ok_button.setFixedSize(30, 28)