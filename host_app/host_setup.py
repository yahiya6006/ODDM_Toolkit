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

from utils import create_oddm_setup_file, connect_to_psql_db, setup_oddm_toolkit_db
import sys
from PySide6.QtWidgets import QApplication
from ui.startup_window import boot_window
from ui.host_setup_ui import SetupPasswordWidget
from utils.database import check_if_admin_exists_in_oddm_db
import json

class ODDM_host_setup:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.boot = boot_window()
        
        self.boot.boot_complete.connect(self.launch_password_ui)

    def launch_password_ui(self):
        self.user_credentials = None
        self.password_ui = SetupPasswordWidget()
        self.password_ui.passwordSubmitted.connect(self.verify_password)
        self.password_ui.userDetailsSubmitted.connect(self.get_user_details)
        self.password_ui.local_storage_selected.connect(self.generate_setup_file)
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
        self.user_credentials = setup_oddm_toolkit_db(oddm_password, self.Admin_psql_password, superuser_email, superuser_name, superuser_password)
        if not self.user_credentials["success"]:
            if self.user_credentials["error_id"] == "ERR-ODDM-STUP-001" or self.user_credentials["error_id"] == "ERR-ODDM-STUP-002":
                self.password_ui.show_error_dialog(self.user_credentials["error"])
                self.password_ui.reset_oddm_db_password_input()
            else:
                self.password_ui.show_error_dialog(self.user_credentials["error"])
                self.password_ui.handle_user_creation_error( self.user_credentials["error_id"] )
            return

        # create_oddm_setup_file(user_credentials["credentials"])

        self.password_ui.stacked_widget.setCurrentIndex(5)

    def generate_setup_file(self, service_json_data, data_storage_path ):
        oddm_setup_data = self.user_credentials["credentials"]
        if service_json_data != "":
            oddm_setup_data["gdrive_service_json_data"] = {"status": True, "data": json.loads( service_json_data ) }
        else:
            oddm_setup_data["gdrive_service_json_data"] = {"status": False, "data": None }
        oddm_setup_data["data_storage_path"] = data_storage_path
        create_oddm_setup_file(oddm_setup_data)
        self.password_ui.stacked_widget.setCurrentIndex(6)

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    setup = ODDM_host_setup()
    setup.run()