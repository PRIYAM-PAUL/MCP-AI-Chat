import os
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from mcp.server import MCPServer


  
# MCP SERVER
  

mcp = MCPServer("Fonada Support Server")


  
# GOOGLE SHEETS CONFIGURATION
  

GOOGLE_CREDENTIALS_FILE = os.getenv(
    "GOOGLE_CREDENTIALS_FILE",
    "credentials/service-account.json"
)

GOOGLE_SHEET_NAME = os.getenv(
    "GOOGLE_SHEET_NAME",
    "MCP"
)

GOOGLE_WORKSHEET_NAME = os.getenv(
    "GOOGLE_WORKSHEET_NAME",
    "Callbacks"
)


  
# CONNECT TO GOOGLE SHEETS
  

def get_worksheet():

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file(
        GOOGLE_CREDENTIALS_FILE,
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open(
        GOOGLE_SHEET_NAME
    )

    worksheet = spreadsheet.worksheet(
        GOOGLE_WORKSHEET_NAME
    )

    return worksheet


  
# TOOL 1
# SEARCH CUSTOMER
  

@mcp.tool()
def search_customer(email: str) -> dict:
    """
    Search for a customer's callback request
    using their email address.
    """

    if not email.strip():

        return {
            "success": False,
            "error": "Customer email is required."
        }

    try:

        worksheet = get_worksheet()

        records = worksheet.get_all_records()

        email_to_find = (
            email.strip().lower()
        )

        matches = []

        for record in records:

            record_email = str(
                record.get("email", "")
            ).strip().lower()

            if record_email == email_to_find:

                matches.append(record)

        if not matches:

            return {
                "success": True,
                "found": False,
                "message": (
                    "No callback request found "
                    "for this email."
                )
            }

        return {
            "success": True,
            "found": True,
            "count": len(matches),
            "callbacks": matches
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }


  
# TOOL 2
# CREATE CALLBACK
  

@mcp.tool()
def create_callback(
    name: str,
    email: str,
    reason: str
) -> dict:
    """
    Create a new customer callback request
    and save it to Google Sheets.
    """

        
    # VALIDATION
        

    if not name.strip():

        return {
            "success": False,
            "error": "Customer name is required."
        }

    if not email.strip():

        return {
            "success": False,
            "error": "Customer email is required."
        }

    if not reason.strip():

        return {
            "success": False,
            "error": "Callback reason is required."
        }


    try:

          
        # CONNECT TO SHEET
          

        worksheet = get_worksheet()


          
        # CREATE CALLBACK ID
          

        existing_rows = worksheet.get_all_values()

        callback_number = max(
            len(existing_rows),
            1
        )

        callback_id = (
            f"CB{callback_number:04d}"
        )


          
        # CURRENT TIME
          

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


          
        # DATA
          

        row = [

            callback_id,

            name.strip(),

            email.strip().lower(),

            reason.strip(),

            "pending",

            created_at
        ]


          
        # ADD ROW TO GOOGLE SHEET
          

        worksheet.append_row(
            row,
            value_input_option="USER_ENTERED"
        )


          
        # RETURN RESULT
          

        callback = {

            "callback_id": callback_id,

            "name": name.strip(),

            "email": email.strip().lower(),

            "reason": reason.strip(),

            "status": "pending",

            "created_at": created_at
        }


        return {

            "success": True,

            "message":
                "Callback created successfully "
                "and saved to Google Sheets.",

            "callback": callback
        }


    except Exception as error:

        return {

            "success": False,

            "error": str(error)
        }


  
# TOOL 3
# LIST CALLBACKS
  

@mcp.tool()
def list_callbacks() -> list:
    """
    Return all customer callback requests
    from Google Sheets.
    """

    try:

        worksheet = get_worksheet()

        records = worksheet.get_all_records()

        return {

            "success": True,

            "count": len(records),

            "callbacks": records
        }

    except Exception as error:

        return {

            "success": False,

            "error": str(error)
        }


  
# SERVER START
  

if __name__ == "__main__":

    mcp.run(
        transport="streamable-http",
        host="127.0.0.1",
        port=8001
    )