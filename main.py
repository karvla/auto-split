from fasthtml.common import *
from dotenv import load_dotenv
from gcsa.event import Event
from gcsa.google_calendar import GoogleCalendar
from gcsa.calendar import CalendarListEntry
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import date
import gspread
import os

load_dotenv()


CALENDAR_URL = os.getenv("CALENDAR_URL")
CALENDAR_ID = os.getenv("CALENDAR_ID")
SHEET_ID = os.getenv("SHEET_ID")

SCOPES = ['https://www.googleapis.com/auth/calendar']

credentials = service_account.Credentials.from_service_account_file(
    'service_account.json', scopes=SCOPES)

app,rt = fast_app()

gc = gspread.service_account(filename="service_account.json")

def get_people() -> List[str]: 
    return gc.open_by_key(SHEET_ID).get_worksheet(3).col_values(1)[1:]

@rt('/')
def get(): return Div(
    add_form(),
    calendar() 
) 

def add_form():
    return Form(
        Group(
            Select(
                *[Option(p) for p in get_people()],
                name="booker"
            ),
            Input(type="date", name="from"), 
            Input(type="date", name="from"), 
            Input(type="text", name="note", placeholder="note"),
            Button("Add")),
                hx_post="/")

def calendar(): return Iframe(src=f'https://calendar.google.com/calendar/embed?src={get_calendar_id()}&ctz=Europe%2FStockholm', width="100%", height="600")

def get_calendar_id():
    return GoogleCalendar(credentials=credentials).get_calendar().calendar_id


def update_calendar():
    gc = GoogleCalendar(credentials=credentials)
    events = list(gc.get_events())

    start = date(2024,8,1)
    end = date(2024,8,2)
    event = Event('Vacation',
                  visibility="public",
              start=start,
              end=end)
    gc.add_event(event)
    print(events)
    for event in gc.get_events():
        print(event)

    

update_calendar()


serve()
