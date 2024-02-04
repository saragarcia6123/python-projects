import random
import tweepy
import gspread
from google.oauth2 import service_account
from gspread.utils import a1_to_rowcol
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time
from pathlib import Path

class ServerHandler(BaseHTTPRequestHandler):

    def run_server():

        PORT = 8000

        # Create an HTTP server with the specified port and request handler
        server = HTTPServer(('localhost', PORT), ServerHandler)

        # Start the server
        print(f"Server started on port {PORT}")
        server.serve_forever()
    
    def stop_server():
        print("Stopping server")
        server.shutdown()
        server.server_close()

    def do_GET(self):
        # Set the response status code
        self.send_response(200)
        
        # Set the content type of the response
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Dynamic Content Example</title>
        </head>
        <body style="background-color: black; color: white;">
            <p>The current date and time is: {current_time}</p>
            <button onclick="stopServer()">Stop Server</button>
            <script>
                function stopServer() {{
                    // Send an HTTP GET request to the server's /stop-server route
                    var xhr = new XMLHttpRequest();
                    xhr.open('GET', '/stop-server', true);
                    xhr.send();
                    
                    // Handle the response from the server
                    xhr.onreadystatechange = function() {{
                        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {{
                            // Display the response from the server
                            console.log(xhr.responseText);
                        }}
                    }};
                }}
            </script>
        </body>
        </html>
        """
        
        # Send the dynamically generated HTML content as the response body
        self.wfile.write(html_content.encode('utf-8'))

        if self.path == '/stop-server':
            self.stop_server()


def authenticate():

    creds_path = Path(__file__).parent /  "../Twitter Bot/Keys/credentials.json"
    
    with creds_path.open() as json_file:
        creds = json.load(json_file)
    
    BEARER_TOKEN = creds["bearer_token"]
    CONSUMER_KEY = creds["consumer_key"]
    CONSUMER_SECRET = creds["consumer_secret"]
    ACCESS_TOKEN = creds["access_token"]
    ACCESS_TOKEN_SECRET = creds["access_token_secret"]

    twt_client = tweepy.Client(bearer_token=BEARER_TOKEN,
                           consumer_key=CONSUMER_KEY,
                           consumer_secret=CONSUMER_SECRET,
                           access_token=ACCESS_TOKEN,
                           access_token_secret=ACCESS_TOKEN_SECRET)
    
    return twt_client

def get_sheet():
    # Authorize Google Sheets API from account key
    creds_path = Path(__file__).parent /   "../Twitter Bot/Keys/service_account.json"
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scope)
    gcp_client = gspread.authorize(creds)

    key_path = Path(__file__).parent /  "../Twitter Bot/Keys/spreadsheet_key.json"
    
    with key_path.open() as json_file:
        key_file = json.load(json_file)
    spreadsheet_key = key_file["key"]

    try:
        sheet = gcp_client.open_by_key(spreadsheet_key).sheet1
    except gspread.exceptions.APIError as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

    return sheet

# Returns a column from a sheet excluding blank values and those starting with $
def read_from_sheet(sheet: gspread.Worksheet, col: str):

    column = a1_to_rowcol(col)[1]
    column_data = sheet.col_values(column)
    filtered_data = [cell for cell in column_data if ((cell != '') and (cell.startswith("$") == False))] # Don't include blank or already posted cells

    return filtered_data

def set_as_posted(sheet: gspread.Worksheet, index_in_arr):

    # Get the index of the cell in from the array in the spreadsheet

    column = a1_to_rowcol('A1')[1]
    column_data = sheet.col_values(column)

    occupied_cells = 0

    index_in_sheet = len(column_data)

    for i in range(1, len(column_data)-1):
        if (column_data[i] != '') and (column_data[i].startswith("$") == False):
            occupied_cells += 1
            if occupied_cells == index_in_arr+1:
                index_in_sheet = i+1
                break

    cell_msg = sheet.cell(index_in_sheet, 1).value

    date = str(datetime.today().strftime("%A, %B %D, %Y")) + " AT " + str(datetime.today().strftime("%H:%M:%S"))
    posted_msg = "$POSTED: " + str(date) + ", MESSAGE:\"" + str(cell_msg) + "\""

    print("UPDATED: Cell (" + str(index_in_sheet) + ", 1) FROM: \"" + str(cell_msg) + "\" TO: \"" + str(posted_msg) + "\"")

    sheet.update_cell(row=index_in_sheet, col=1, value=posted_msg)

def schedule_post(sheet: gspread.Worksheet):

    #TODO: 

    return

def parse_date(date: str):

    #TODO

    

    return

def post_to_twitter(twt_client: tweepy.Client):  
    sheet = get_sheet()
    msg_list = read_from_sheet(sheet, 'A1')
    if len(msg_list) == 0:
        print("No messages available")
        return
    msg_index = random.randint(0, len(msg_list)-1)
    msg_text = msg_list[msg_index]
    set_as_posted(sheet, msg_index)
    #twt_client.create_tweet(text=msg_text)

def check_for_updates():
    while True:
        try:
            print("hello")
            time.sleep(5)
        except Exception as e:
            print("An error occurred:", e)
            
            # Wait for 30 seconds before polling again
            time.sleep(30)

#GCP schedule trigger
def main(event, context):
    print("Received event: ", event)
    twt_client = authenticate()
    if twt_client != None:
        print("Authenticated")
        post_to_twitter(twt_client)
        
    return {
        'statusCode': 200,
        'body': 'Function executed successfully'
    }

if __name__ == "__main__":
    #PORT = 8000
    #server = HTTPServer(('localhost', PORT), ServerHandler)
    #print(f"Server started on port {PORT}")
    #server.serve_forever()

    #server_thread = threading.Thread(target=check_for_updates)
    #server_thread.start()

    twt_client = authenticate()

    if twt_client != None:
        post_to_twitter(twt_client)