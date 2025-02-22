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