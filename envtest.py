from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent / '.env'

if not load_dotenv(dotenv_path=env_path):
    print("No .env file found. Please create one !")
    exit(1)
    
print("HOST: ", os.getenv("HOST"))
print("PORT: ", os.getenv("PORT"))
print("RTMP_IP: ", os.getenv("RTMP_IP"))
print("RTMP_PORT: ", os.getenv("RTMP_PORT"))
print("VIDEO_SAVE_PATH: ", os.getenv("VIDEO_SAVE_PATH"))
print("DB_HOST: ", os.getenv("DB_HOST"))
print("DB_NAME: ", os.getenv("DB_NAME"))
