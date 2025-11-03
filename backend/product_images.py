from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from passlib.hash import bcrypt
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates


router = APIRouter()
load_dotenv() # .env 파일 로드


DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # 포트는 정수형으로 변환

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

def products_images(product_id: int):
    try:
        sql = "SELECT * FROM product_images WHERE product_id= %s"
        connection = get_db_con()
        with connection.cursor() as cursor:
            cursor.execute(sql, (product_id,))
            result = cursor.fetchall()
            print(type(result))
            print(result)
            return result
    except Exception as e:
        print(f"Error: {e}")
        return HTMLResponse(f"Error: {e}")