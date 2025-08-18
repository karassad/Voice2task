import os
from dotenv import load_dotenv


load_dotenv()
# Configuration for the Voice2Task Telegram bot
BOT_TOKEN = os.getenv('BOT_TOKEN')

WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Google OAuth credentials
GOOGLE_CLIENT_ID= os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPES = ['https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/calendar'] #https://developers.google.com/workspace/calendar/api/auth

FIREBASE_SERVICE_ACCOUNT_KEY_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

FERNET_KEY = os.getenv('FERNET_KEY')

GEMINI_API_KEY = os.getenv('API_GEMINI_KEY')
GEMINI_API_URL = os.getenv('API_GEMINI_URL')