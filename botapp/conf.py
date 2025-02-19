import os
from dotenv import load_dotenv

load_dotenv()

YTOKEN = os.environ.get("YTOKEN")
TOKEN = os.environ.get("TOKEN")
adm = os.environ.get("ADMINS")
ADMINS = [int(admin_id) for admin_id in adm.split(',')]
url = os.environ.get("url")
TOKEN = os.environ.get("TOKEN")
user = os.environ.get("user")
password = os.environ.get("passw")
host = os.environ.get("host")
port = os.environ.get("port")
db = os.environ.get("db")