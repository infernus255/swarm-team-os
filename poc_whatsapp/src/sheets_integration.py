
import gspread
from google.oauth2.service_account import Credentials

class GoogleSheetsManager:
    def __init__(self, credentials_file, sheet_name):
        self.credentials = Credentials.from_service_account_file(credentials_file)
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.file",
        ]
        self.credentials = self.credentials.with_scopes(self.scope)
        self.client = gspread.authorize(self.credentials)
        self.sheet = self.client.open(sheet_name).sheet1 # Assuming the first sheet

    async def add_price_entry(self, product, old_price, new_price, timestamp):
        row = [product, old_price, new_price, timestamp]
        self.sheet.append_row(row)
        return True
