from dotenv import load_dotenv
import os

load_dotenv()

APP_VERSION = os.getenv('APP_VERSION')# app version 

UUID_PAYMENT = os.getenv('UUID_PAYMENT')
AES_KEY = bytes(os.getenv('AES_KEY'), 'utf-8')
USER_ID = os.getenv('USER_ID')
X_UID = os.getenv('X_UID')
PRIV_KEY = os.getenv('PRIV_KEY')