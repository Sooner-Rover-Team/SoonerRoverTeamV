import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'credentials.json'

def get_calendar_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

################################################################

def get_list_event(eventnumber,tmin,tmax):
    service = get_calendar_service()
    # Call the Calendar API


    events_result = service.events().list(calendarId='primary',
                                        timeMin=tmin,
                                        timeMax=tmax,
                                        maxResults=eventnumber,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(events)
    dictlist = []
    if not events:
        print('No upcoming events found.')
    print(f'Getting List of {len(events)} events')
    for event in events:

        end = event['end'].get('dateTime', event['end'].get('date'))
        #end_time = datetime.strftime(dtparse(end), format=tmfmt)
        start = event['start'].get('dateTime', event['start'].get('date'))
        #start_time = datetime.strftime(dtparse(start), format=tmfmt)
        event_title_summary = event['summary']
        event_description = event.get('description', 'Meeting')
        html_link = event['htmlLink']
        dictlist.append({'start_datetime': start,
                        'end_datetime':end,
                        'eventtitle' : event_title_summary,
                        'html_link' : html_link,
                        'event_desc': event_description})
    return(dictlist)