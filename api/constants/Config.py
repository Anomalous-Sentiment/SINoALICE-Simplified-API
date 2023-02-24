from dotenv import load_dotenv
import os

load_dotenv()

APP_VERSION = '42.1.0' # app version

UUID_PAYMENT = os.getenv('UUID_PAYMENT')
AES_KEY = bytes(os.getenv('AES_KEY'), 'utf-8')
print(AES_KEY)
USER_ID = os.getenv('USER_ID')
X_UID = os.getenv('X_UID')
PRIV_KEY = os.getenv('PRIV_KEY')