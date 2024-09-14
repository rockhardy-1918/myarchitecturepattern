# models.py
from pydantic import BaseModel
from typing import List, Dict
import pygsheets
from fastapi.security.api_key import APIKeyHeader, APIKey
from google.cloud import secretmanager
from google.oauth2 import service_account
import json
import pytz
from datetime import datetime

class Terrtories(BaseModel):
    area: str
    sheet_name: str

def get_google_sheets_credentials():
    project_id = "odin-backup-432014"
    secret_id = 'SHEET'
    client = secretmanager.SecretManagerServiceClient()
    secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": secret_name})
    secret_payload = response.payload.data.decode("UTF-8")
    credentials_info = json.loads(secret_payload)
    return service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )

def load_data_from_google_sheets(sheet_name: str) -> List[dict]:
    credentials = get_google_sheets_credentials()
    gc = pygsheets.authorize(custom_credentials=credentials)
    sh = gc.open_by_key("1Z4WzY2_WqjXk6G0nFel9lQiqKQaz1RPhNuilgRjRaSM")
    worksheet = sh.worksheet_by_title(sheet_name)
    data = worksheet.get_all_records()
    return data

def load_data_from_google_sheets2(sheet_name: str) -> List[dict]:
    credentials = get_google_sheets_credentials()
    gc = pygsheets.authorize(custom_credentials=credentials)
    sh = gc.open_by_key("1rIcrh0unYHwh3ufuj79Xfj_KPJTxgU_xid-_wnEFBOs")
    worksheet = sh.worksheet_by_title(sheet_name)
    data = worksheet.get_all_records()
    return data

def get_current_time(timezone: str) -> str:
    tz = pytz.timezone(timezone)
    return datetime.now(tz).strftime("%m/%d/%Y %I:%M:%S %p")
API_KEY = "your-secret-api-key"
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    
    
pool = None

dbp={
    'NA':{
        'db':'onehub_db_testing'
    },
    'AU':{
        'db':'onehub_db_testing_au'
    }
}
async def get_db_pool():
    global pool
    if pool is None:
        pool = await aiomysql.create_pool(
            host='34.29.110.213',
            port=3306,
            user="insert_ac",
            password='google@123',
            db='onehub_db_testing',
            minsize=1,
            maxsize=10
        )
    return pool
