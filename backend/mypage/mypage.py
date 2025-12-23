from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from passlib.hash import bcrypt
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi import Request
from fastapi.templating import Jinja2Templates
import requests

from fastapi.responses import RedirectResponse

router = APIRouter()
load_dotenv() # .env 파일 로드

# DB 연결 설정
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER") 
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# DB 연결
def get_db_con():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

# 템플릿 설정
templates = Jinja2Templates(directory="templates")


def get_user_name(user_id: int):
    connection = get_db_con()
    with connection.cursor() as cursor:
        try:
            sql = "SELECT username FROM users WHERE id=%s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            username = result['username']
            connection.close()
            if result:
                return username
            return None
        except Exception as e:
            print(f"Error fetching username: {e}")
            return None