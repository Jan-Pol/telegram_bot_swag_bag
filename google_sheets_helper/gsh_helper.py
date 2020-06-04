import gspread
from oauth2client.service_account import ServiceAccountCredentials


def update_google_sheet(data):
    try:

        scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
                 "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("google_sheets_helper/creds.json", scope)

        client = gspread.authorize(creds)
        sheet = client.open("data1").sheet1
        sheet.append_row(data)
    except SystemError:
        return
    return
