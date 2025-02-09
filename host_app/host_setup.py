from utils import create_oddm_setup_file, get_oddm_setup_credentials, connect_to_psql_db, setup_oddm_toolkit_db
import sys
from PySide6.QtWidgets import QApplication
from ui.startup_window import boot_window
from ui.host_setup_ui import SetupPasswordWidget
from utils.database import check_if_admin_exists_in_oddm_db

class ODDM_host_setup:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.boot = boot_window()
        
        self.boot.boot_complete.connect(self.launch_password_ui)

    def launch_password_ui(self):
        self.password_ui = SetupPasswordWidget()
        self.password_ui.passwordSubmitted.connect(self.verify_password)
        self.password_ui.userDetailsSubmitted.connect(self.get_user_details)
        self.password_ui.show()

    def verify_password(self, password):
        """Verifies the PostgreSQL password."""
        if connect_to_psql_db(password):
            print("✅ Password correct! Proceeding with setup...")
            self.Admin_psql_password = password
            if check_if_admin_exists_in_oddm_db(password):
                self.password_ui.stacked_widget.setCurrentIndex(4)
            else:
                self.password_ui.stacked_widget.setCurrentIndex(1)
        else:
            self.password_ui.show_error_dialog("Incorrect password. Please try again.")
            self.password_ui.reset_psql_password_input()

    def get_user_details(self, oddm_password, superuser_email, superuser_name, superuser_password ):
        user_credentials = setup_oddm_toolkit_db(oddm_password, self.Admin_psql_password, superuser_email, superuser_name, superuser_password)
        if not user_credentials["success"]:
            if user_credentials["error_id"] == "ERR-ODDM-STUP-001":
                self.password_ui.show_error_dialog(user_credentials["error"])
                self.password_ui.reset_oddm_db_password_input()
            else:
                self.password_ui.show_error_dialog(user_credentials["error"])
                self.password_ui.handle_user_creation_error( user_credentials["error_id"] )
            return

        create_oddm_setup_file(user_credentials["credentials"])

        self.password_ui.stacked_widget.setCurrentIndex(5)

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    setup = ODDM_host_setup()
    setup.run()