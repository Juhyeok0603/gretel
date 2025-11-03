from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from passlib.hash import bcrypt
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
import json
from decimal import Decimal


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



def products_info(product_id: int):
    print(product_id)
    try:
        you_want = "products"
        sql = f"SELECT * FROM {you_want} WHERE product_id= %s"
        connection = get_db_con()
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {you_want} WHERE id= %s",(product_id)) # products
            result = cursor.fetchone()
            if isinstance(result.get("price"), Decimal):
                result["price"] = float(result["price"])

    # categories 문자열 → 리스트
            if isinstance(result.get("categories"), str):
                try:
                    result["categories"] = json.loads(result["categories"])
                except json.JSONDecodeError:
                    result["categories"] = []
            if isinstance(result.get("sizes"), str):
                try:
                    result["sizes"] = json.loads(result["sizes"])
                except json.JSONDecodeError:
                    result["sizes"] = []
            print(type(result))
            print(result)
            return result
    except Exception as e:
        print(f"Error: {e}")
        return HTMLResponse(f"Error: {e}")