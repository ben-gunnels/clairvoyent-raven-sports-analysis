# create_oauth_file.py
from yahoo_oauth import OAuth2
import json
import os
from dotenv import load_dotenv

load_dotenv()

creds = {"consumer_key": os.getenv("YAHOO_DATA_API_CLIENT_ID"), "consumer_secret": os.getenv("YAHOO_DATA_API_CLIENT_SECRET")}
with open("oauth2.json", "w") as f:
    f.write(json.dumps(creds))

# This will guide you through browser auth on first run and cache tokens.
oauth = OAuth2(None, None, from_file="oauth2.json")
