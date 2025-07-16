import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from utils.logger import log_entry

class GmailService:
    def __init__(self):
        try: 
            SCOPES = [
                'https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.labels',
                'https://www.googleapis.com/auth/gmail.modify',
                'https://www.googleapis.com/auth/gmail.send',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'
            ]
            self.creds = None  # ← importante
            if os.path.exists('config/token.json'):
                self.creds = Credentials.from_authorized_user_file('config/token.json', SCOPES)
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file('config/credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)
                # Guardar token
                with open('config/token.json', 'w') as token:
                    token.write(self.creds.to_json())
            #Add log memory: log_entry(message_id, process_name, level, code, message)
            log_entry('None', 'GmailService', 'SUCCESS', '0000', f'Fetch creds OK')

        except Exception as e:
            #Add log memory: log_entry(message_id, process_name, level, code, message)
            log_entry('None', 'GmailService', 'FATAL', '0001', f'❌ Error fetching creds: {e}')

    def get_creds(self):
        return self.creds
