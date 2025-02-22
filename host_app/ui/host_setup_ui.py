# MIT License
# 
# Copyright (c) 2025 Yahiya Mulla
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from PySide6.QtCore import Qt, QSize, QRect, QCoreApplication, QMetaObject, Signal
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QSpacerItem, QSizePolicy, QMessageBox, QStackedWidget, QHBoxLayout, QFileDialog, QCheckBox
from PySide6.QtGui import QColor, QPalette, QIcon, QPixmap
from .theme import *
import re
import os
from pathlib import Path
import json
import utils.gdrive as gdrive

# Get the absolute path of the current file (the script inside 'ui' folder)
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Moves 3 levels up to project root

# Custom QLineEdit to handle backspace key press
class PasswordLineEdit(QLineEdit):
    enterPressed = Signal()  # Custom signal to trigger submit button

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Error_State = False

    def keyPressEvent(self, event):
        if self.Error_State:
            self.reset_state()
            self.Error_State = False

        if event.key() == Qt.Key_Backspace:
            self.clear()  # Clear the input field when backspace is pressed
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):  # Check for Enter key
            self.enterPressed.emit()  # Emit the signal when Enter is pressed
        else:
            super().keyPressEvent(event)  # Call the original key event handler
    
    def set_error_state(self):
        self.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {ERROR_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)
        self.Error_State = True

    def set_ok_state(self):
        self.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {SUCCESS_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)

    def reset_state(self):
        self.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)

class SimpleLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Error_State = False

    def keyPressEvent(self, event):
        if self.Error_State:
            self.reset_state()
            self.Error_State = False

        super().keyPressEvent(event)

    def set_error_state(self):
        self.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {ERROR_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)
        self.Error_State = True

    def set_ok_state(self):
        self.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {SUCCESS_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)

    def reset_state(self):
        self.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)

class SetupPasswordWidget(QWidget):
    passwordSubmitted = Signal(str)
    userDetailsSubmitted = Signal(str, str, str, str)
    local_storage_selected = Signal(str, str)

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
        self.re_verify_page = self.create_user_password_re_verify_page()
        self.setup_already_done_page = self.get_user_concent_for_setup_alreasdy_done()
        self.admin_already_exists_page = self.get_user_concent_for_admin_already_exists()
        self.setup_storage_page = self.show_setup_storage_page()
        self.setup_completed_page = self.show_setup_completed_page()

        self.stacked_widget.addWidget(self.password_page)
        self.stacked_widget.addWidget(self.user_page)
        self.stacked_widget.addWidget(self.re_verify_page)
        self.stacked_widget.addWidget(self.setup_already_done_page)
        self.stacked_widget.addWidget(self.admin_already_exists_page)
        self.stacked_widget.addWidget(self.setup_storage_page)
        self.stacked_widget.addWidget(self.setup_completed_page)

        if os.path.exists(".oddm_setup_config"):
            self.stacked_widget.setCurrentIndex(3)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def show_setup_completed_page(self):
        page = QWidget()
        # Layout
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)  # Add padding around the edges
        layout.setSpacing(15)  # Set spacing between widgets

        label = QLabel()
        label.setObjectName("instruction_label")
        label.setText("The host setup has been successfully completed.")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            color: {TEXT_PRIMARY_COLOR}; 
            font-size: {TEXT_SIZE_HEADING}; 
            font-weight: bold;
            font-family: {TEXT_FONT_FAMILY};
        """)
        layout.addWidget(label)

        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        button = QPushButton()
        button.setObjectName("final_button")
        button.setText("Close")
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        button.setFixedSize(80, 28)
        layout.addWidget(button, alignment=Qt.AlignCenter)

        button.clicked.connect(lambda: self.close())

        page.setLayout(layout)
        return page

    def get_user_concent_for_setup_alreasdy_done(self):
        page = QWidget()
        # Layout
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 0, 20, 20)  # Add padding around the edges
        layout.setSpacing(15)  # Set spacing between widgets

        label = QLabel()
        label.setObjectName("instruction_label")
        label.setText("ODDM Toolkit setup has already been completed on this system. Do you still want to proceed with the setup ?")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            color: {TEXT_PRIMARY_COLOR}; 
            font-size: {TEXT_SIZE_HEADING}; 
            font-weight: bold;
            font-family: {TEXT_FONT_FAMILY};
        """)
        layout.addWidget(label)

        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        yes_button = QPushButton()
        yes_button.setObjectName("yes_button")
        yes_button.setText("Yes, Continue")
        yes_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        yes_button.setFixedSize(110, 28)
        button_layout.addWidget(yes_button, alignment=Qt.AlignCenter)

        no_button = QPushButton()
        no_button.setObjectName("no_button")
        no_button.setText("No, Close")
        no_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ERROR_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        no_button.setFixedSize(110, 28)
        button_layout.addWidget(no_button, alignment=Qt.AlignCenter)

        no_button.clicked.connect(lambda: self.close())
        yes_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        layout.addLayout(button_layout)
        page.setLayout(layout)
        return page

    def get_user_concent_for_admin_already_exists(self):
        page = QWidget()
        # Layout
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)  # Add padding around the edges
        layout.setSpacing(15)  # Set spacing between widgets

        label = QLabel()
        label.setObjectName("instruction_label")
        message = ("The system has detected that an admin account has already been set up. "
               "To proceed, please enter the database password for verification.\n\n"
               "By continuing, you acknowledge that you are adding a new admin user. "
               "A user cannot be created if the credentials already exist.\n\n"
               "Creating an additional admin account is at your own risk.\n"
               "Do you want to continue?")
        label.setText(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        label.setMaximumWidth(380)  # Prevent excessive stretching
        label.setStyleSheet(f"""
            color: {TEXT_PRIMARY_COLOR}; 
            font-size: {TEXT_SIZE_INPUT_FEILD}; 
            font-weight: bold;
            font-family: {TEXT_FONT_FAMILY};
        """)
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        yes_button = QPushButton()
        yes_button.setObjectName("yes_button")
        yes_button.setText("Yes, Continue")
        yes_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {SUCCESS_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        yes_button.setFixedSize(110, 28)
        button_layout.addWidget(yes_button, alignment=Qt.AlignCenter)

        no_button = QPushButton()
        no_button.setObjectName("no_button")
        no_button.setText("No, Close")
        no_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ERROR_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        no_button.setFixedSize(110, 28)
        button_layout.addWidget(no_button, alignment=Qt.AlignCenter)

        no_button.clicked.connect(lambda: self.close())
        yes_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addLayout(button_layout)
        page.setLayout(layout)
        return page
        
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
            font-weight: bold;
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
                font-weight: bold;
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

    def reset_psql_password_input(self):
        """Resets the PostgreSQL password input field."""
        self.password_input.set_error_state()

        # Re-enable input fields
        self.password_input.setReadOnly(False)
        self.password_input.clear()
        self.submit_button.setEnabled(True)

    def show_error_dialog(self, message):
        """Displays an error message."""
        error_dialog = ErrorDialog(message, self)
        error_dialog.exec_()

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

        self.oddm_db_password_input = PasswordLineEdit()
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
            font-weight: bold;
        """)
        self.oddm_db_password_input.setFixedWidth(250)
        layout.addWidget(self.oddm_db_password_input, alignment=Qt.AlignCenter)

        self.superuser_email_input = SimpleLineEdit()
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
            font-weight: bold;
        """)
        self.superuser_email_input.setFixedWidth(250)
        layout.addWidget(self.superuser_email_input, alignment=Qt.AlignCenter)

        self.superuser_username_input = SimpleLineEdit()
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
            font-weight: bold;
        """)
        self.superuser_username_input.setFixedWidth(250)
        layout.addWidget(self.superuser_username_input, alignment=Qt.AlignCenter)

        self.superuser_password_input = PasswordLineEdit()
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
            font-weight: bold;
        """)
        self.superuser_password_input.setFixedWidth(250)
        layout.addWidget(self.superuser_password_input, alignment=Qt.AlignCenter)

        # Submit button
        self.user_next_button = QPushButton()
        self.user_next_button.setObjectName("user_next_button")
        self.user_next_button.setText("Next")
        self.user_next_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_BUTTON_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        self.user_next_button.setFixedSize(80, 28)
        layout.addWidget(self.user_next_button, alignment=Qt.AlignCenter)
        self.user_next_button.clicked.connect(self.submit_user_details)

        page.setLayout(layout)
        return page

    def submit_user_details(self):
        oddm_password = self.oddm_db_password_input.text()
        superuser_email = self.superuser_email_input.text()
        superuser_name = self.superuser_username_input.text()
        superuser_password = self.superuser_password_input.text()

        if not oddm_password or not superuser_email or not superuser_name or not superuser_password:
            self.show_error_dialog("All fields are required.")

            if not oddm_password:
                self.oddm_db_password_input.set_error_state()
            if not superuser_email:
                self.superuser_email_input.set_error_state()
            if not superuser_name:
                self.superuser_username_input.set_error_state()
            if not superuser_password:
                self.superuser_password_input.set_error_state()

            return

        # Validate email format directly in this function
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, superuser_email):
            self.show_error_dialog("Invalid email address. Please enter a valid email.")

            self.superuser_email_input.set_error_state()

            return

        self.stacked_widget.setCurrentIndex(2)
    
    def create_user_password_re_verify_page(self):
        page = QWidget()
        # Layout
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)  # Add padding around the edges
        layout.setSpacing(15)

        label = QLabel()
        label.setObjectName("Re_enter_password_label")
        label.setText("Re-enter your passwords for verification")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            color: {TEXT_PRIMARY_COLOR}; 
            font-size: {TEXT_SIZE_HEADING}; 
            font-weight: bold;
            font-family: {TEXT_FONT_FAMILY};
        """)
        layout.addWidget(label)

        self.re_enter_oddm_db_password_input = PasswordLineEdit()
        self.re_enter_oddm_db_password_input.setObjectName("re_enter_oddm_db_password_input")
        self.re_enter_oddm_db_password_input.setPlaceholderText("Re-enter ODDM DB Preferred Password")
        self.re_enter_oddm_db_password_input.setEchoMode(QLineEdit.Password)  # Hide password input
        self.re_enter_oddm_db_password_input.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)
        self.re_enter_oddm_db_password_input.setFixedWidth(250)
        layout.addWidget(self.re_enter_oddm_db_password_input, alignment=Qt.AlignCenter)

        self.re_enter_superuser_password_input = PasswordLineEdit()
        self.re_enter_superuser_password_input.setObjectName("re_enter_superuser_password_input")
        self.re_enter_superuser_password_input.setPlaceholderText("Re-enter Superuser Password")
        self.re_enter_superuser_password_input.setEchoMode(QLineEdit.Password)  # Hide password input
        self.re_enter_superuser_password_input.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)
        self.re_enter_superuser_password_input.setFixedWidth(250)
        layout.addWidget(self.re_enter_superuser_password_input, alignment=Qt.AlignCenter)

        # Submit button
        self.re_verify_submit_button = QPushButton()
        self.re_verify_submit_button.setObjectName("re_verify_submit_button")
        self.re_verify_submit_button.setText("Submit")
        self.re_verify_submit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_BUTTON_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        self.re_verify_submit_button.setFixedSize(80, 28)
        layout.addWidget(self.re_verify_submit_button, alignment=Qt.AlignCenter)
        self.re_verify_submit_button.clicked.connect(self.check_for_password_mismatch)

        page.setLayout(layout)
        return page

    def check_for_password_mismatch(self):
        oddm_password = self.oddm_db_password_input.text()
        superuser_password = self.superuser_password_input.text()

        re_enter_oddm_password = self.re_enter_oddm_db_password_input.text()
        re_enter_superuser_password = self.re_enter_superuser_password_input.text()

        # check for wrong password
        if ( oddm_password != re_enter_oddm_password ) and ( superuser_password != re_enter_superuser_password ):
            self.show_error_dialog("Both passwords do not match")
            self.oddm_db_password_input.set_error_state()
            self.oddm_db_password_input.clear()
            self.superuser_password_input.set_error_state()
            self.superuser_password_input.clear()
            self.re_enter_oddm_db_password_input.clear()
            self.re_enter_superuser_password_input.clear()

            self.stacked_widget.setCurrentIndex(1)
        elif oddm_password != re_enter_oddm_password:
            self.show_error_dialog("ODDM DB password do not match")
            self.oddm_db_password_input.set_error_state()
            self.oddm_db_password_input.clear()
            self.re_enter_oddm_db_password_input.clear()
            self.re_enter_superuser_password_input.clear()

            self.stacked_widget.setCurrentIndex(1)
        elif superuser_password != re_enter_superuser_password:
            self.show_error_dialog("Superuser password do not match")
            self.superuser_password_input.set_error_state()
            self.superuser_password_input.clear()
            self.re_enter_superuser_password_input.clear()

            self.stacked_widget.setCurrentIndex(1)
        elif ( oddm_password == re_enter_oddm_password ) and ( superuser_password == re_enter_superuser_password ):
            self.userDetailsSubmitted.emit(oddm_password, self.superuser_email_input.text(), self.superuser_username_input.text(), superuser_password)

    def handle_user_creation_error(self, error_id):
        if error_id == "ERR-USR-001":
            self.superuser_email_input.set_error_state()
            self.superuser_username_input.set_error_state()
        elif error_id == "ERR-USR-002":
            self.superuser_username_input.set_error_state()
        elif error_id == "ERR-USR-003":
            self.superuser_email_input.set_error_state()

        # at this point connection to the database has been established. We can skip the password verification page.
        self.oddm_db_password_input.set_ok_state()
        self.oddm_db_password_input.setEnabled(False)

        self.re_enter_oddm_db_password_input.set_ok_state()
        self.re_enter_oddm_db_password_input.setEnabled(False)

        self.superuser_password_input.clear()
        self.re_enter_superuser_password_input.clear()

        self.stacked_widget.setCurrentIndex(1)

    def reset_oddm_db_password_input(self):
        self.oddm_db_password_input.set_error_state()
        self.oddm_db_password_input.clear()

        # Reset the re-verification page
        self.re_enter_oddm_db_password_input.clear()
        self.re_enter_superuser_password_input.clear()

        self.stacked_widget.setCurrentIndex(1)

    def show_setup_storage_page(self):
        page = QWidget()
        # Layout
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 5, 20, 5)
        layout.setSpacing(15)

        default_path = Path( BASE_DIR ) / "ODDM_data"

        local_storage_label = QLabel("Select Local Storage Location:")
        local_storage_label.setStyleSheet(f"""
            color: {TEXT_PRIMARY_COLOR}; 
            font-size: {TEXT_SIZE_HEADING}; 
            font-weight: bold;
            font-family: {TEXT_FONT_FAMILY};
        """)
        layout.addWidget(local_storage_label)

        self.local_storage_path = SimpleLineEdit()
        self.local_storage_path.setObjectName("local_storage_path")
        self.local_storage_path.setPlaceholderText("Select local storage path")
        self.local_storage_path.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)
        self.local_storage_path.setText( str(default_path) )

        browse_local_button = QPushButton()
        browse_icon_pth = str( BASE_DIR / "assets" / "icons" / "browse_folder_ico.png" )
        icon = QIcon(QPixmap(browse_icon_pth).scaled(32, 32))
        browse_local_button.setIcon(icon)
        browse_local_button.setIconSize(QSize(26, 26))
        browse_local_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_BUTTON_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        browse_local_button.setFixedSize(34, 34)
        browse_local_button.clicked.connect(self.select_local_folder)

        # Arrange Local Storage in a Horizontal Layout
        local_layout = QHBoxLayout()
        local_layout.addWidget(self.local_storage_path)
        local_layout.addWidget(browse_local_button)
        layout.addLayout(local_layout)

        # 2. Google Drive Backup (Optional)
        self.enable_cloud_checkbox = QCheckBox("Enable Google Drive Backup")
        self.enable_cloud_checkbox.stateChanged.connect(self.toggle_cloud_options)
        self.enable_cloud_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {TEXT_PRIMARY_COLOR};
                font-size: {TEXT_SIZE_INPUT_FEILD};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
                spacing: 8px;
            }}
        """)
        layout.addWidget(self.enable_cloud_checkbox)

        # Google Drive JSON File Selection
        self.service_account_path = SimpleLineEdit()
        self.service_account_path.setObjectName("local_storage_path")
        self.service_account_path.setPlaceholderText("Select service account JSON")
        self.service_account_path.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)
        self.service_account_path.setVisible(False)

        self.browse_json_button = QPushButton()
        self.browse_json_button.setVisible(False)
        browse_file_pth = str( BASE_DIR / "assets" / "icons" / "add_file_json.png" )
        file_icon = QIcon(QPixmap(browse_file_pth).scaled(32, 32))
        self.browse_json_button.setIcon(file_icon)
        self.browse_json_button.setIconSize(QSize(26, 26))
        self.browse_json_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_BUTTON_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        self.browse_json_button.setFixedSize(34, 34)
        self.browse_json_button.clicked.connect(self.select_service_json)

        # Arrange JSON Selection in a Horizontal Layout
        json_layout = QHBoxLayout()
        json_layout.addWidget(self.service_account_path)
        json_layout.addWidget(self.browse_json_button)
        layout.addLayout(json_layout)

        # Google Drive Folder ID
        self.folder_id_input = SimpleLineEdit()
        self.folder_id_input.setObjectName("folder_id_input")
        self.folder_id_input.setPlaceholderText("Enter Google Drive Folder ID")
        self.folder_id_input.setVisible(False)
        self.folder_id_input.setStyleSheet(f"""
            background-color: {INPUT_BG_COLOR};
            border: 2px solid {INPUT_BORDER_COLOR};
            color: {TEXT_PRIMARY_COLOR};
            padding: 5px;
            font-size: {TEXT_SIZE_INPUT_FEILD};
            border-radius: 4px;
            font-family: {TEXT_FONT_FAMILY};
            font-weight: bold;
        """)
        layout.addWidget(self.folder_id_input)

        submit_button = QPushButton()
        submit_button.setObjectName("submit_button_storage")
        submit_button.setText("Submit")
        submit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_BUTTON_COLOR};
                color: {TEXT_PRIMARY_COLOR};
                border-radius: 4px;
                padding: 5px;
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_COLOR};  /* Hover effect */
            }}
            QPushButton:pressed {{
                background-color: {ACTIVE_COLOR};  /* Click effect */
            }}
        """)
        submit_button.setFixedSize(80, 28)
        layout.addWidget(submit_button, alignment=Qt.AlignCenter)

        submit_button.clicked.connect(self.setup_storage_submit)

        page.setLayout(layout)
        return page

    def select_local_folder(self):
        """Open a file dialog for local storage selection."""
        folder = QFileDialog.getExistingDirectory(self, "Select Storage Directory", str( BASE_DIR ) )
        if folder:
            selected_path = Path(folder) / "ODDM_data"
            self.local_storage_path.setText( str( selected_path ) )

    def toggle_cloud_options(self):
        """Enable or disable cloud storage options based on checkbox state."""
        if self.enable_cloud_checkbox.isChecked():
            enable = True
            self.setFixedSize(400, 300)
        else:
            enable = False
            self.setFixedSize(400, 250)

        self.service_account_path.setVisible(enable)
        self.browse_json_button.setVisible(enable)
        self.folder_id_input.setVisible(enable)

    def is_selected_json_valid(self):
        """Check if the selected JSON file is valid."""
        json_path = self.service_account_path.text()

        try:
            with open(json_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            self.show_error_dialog("The selected JSON file is invalid.")
            self.service_account_path.set_error_state()
            self.service_account_path.clear()
            return False

        required_keys = {
            "type", "project_id", "private_key_id", "private_key",
            "client_email", "client_id", "auth_uri", "token_uri",
            "auth_provider_x509_cert_url", "client_x509_cert_url", "universe_domain"
        }

        # Find missing keys
        missing_keys = required_keys - data.keys()

        if missing_keys:
            self.show_error_dialog("The selected JSON file is missing required keys. missing keys: " + ", ".join(missing_keys))
            self.service_account_path.set_error_state()
            self.service_account_path.clear()
            return False

        # Check if "type" is "service_account"
        if data.get("type") != "service_account":
            self.show_error_dialog("The selected JSON file is not a service account.")
            self.service_account_path.set_error_state()
            self.service_account_path.clear()
            return False

        return True

    def select_service_json(self):
        """Open a file dialog for selecting the Google service account JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Service Account JSON", "", "JSON Files (*.json)")
        if file_path:
            self.service_account_path.reset_state()
            self.service_account_path.setText(file_path)
            self.is_selected_json_valid()

    def setup_storage_submit(self):
        """Submit the storage options."""
        local_path = self.local_storage_path.text()
        service_json_file = self.service_account_path.text()
        folder_id = self.folder_id_input.text()

        # creates the selected local path
        os.makedirs(local_path, exist_ok=True)

        # Google Drive Backup is checked
        if self.enable_cloud_checkbox.isChecked():
            gdrive_res = gdrive.establish_connection( service_json_file )
            if gdrive_res['success']:
                id_check_res = gdrive.check_if_gdrive_folder_exists( gdrive_res['gdrive_connection'], folder_id )
                if id_check_res['success']:
                    with open(service_json_file, "r") as f:
                        service_json_data = json.load(f)
                    self.local_storage_selected.emit( json.dumps(service_json_data), local_path )
                else:
                    self.show_error_dialog( id_check_res['error'] )
                    return
            else:
                self.show_error_dialog( gdrive_res['error'] )
                return
        else:
            self.local_storage_selected.emit( "", local_path )

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
                font-size: {TEXT_SIZE_BUTTONS};
                font-family: {TEXT_FONT_FAMILY};
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {ERROR_COLOR};
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
        ok_button.setFixedSize(32, 28)