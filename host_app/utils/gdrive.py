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

from google.oauth2 import service_account
from googleapiclient.discovery import build

# Define Google Drive API Scope
SCOPES = ["https://www.googleapis.com/auth/drive"]

def establish_connection( service_json_file, service_json_data=None ):
    """Establish a connection to Google Drive using a service account."""
    try:
        if service_json_data:
            creds = service_account.Credentials.from_service_account_info(service_json_data, scopes=SCOPES)
        else:
            creds = service_account.Credentials.from_service_account_file(service_json_file, scopes=SCOPES)
        drive_service = build("drive", "v3", credentials=creds)
        return { "success": True, "gdrive_connection": drive_service }
    except Exception as e:
        return { "success": False, "error": f"Failed to establish connection: {e}" }

def check_if_gdrive_folder_exists(drive_service, folder_id):
    """Check if a Google Drive folder exists."""
    try:
        response = drive_service.files().get(fileId=folder_id, fields="id, name").execute()
        if "id" in response:
            return { "success": True }
    except HttpError as e:
        return { "success": False, "error": f"Google Drive API error: {e}" }
    except Exception as e:
        return { "success": False, "error": f"Failed to check folder: {e}" }