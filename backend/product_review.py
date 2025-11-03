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

def product_reviews(product_id: int):
    try:
        connection = get_db_con()
        with connection.cursor() as cursor:
            # 1️⃣ product_reviews 테이블에서 리뷰 가져오기
            cursor.execute("SELECT * FROM product_reviews WHERE product_id = %s", (product_id,))
            reviews = cursor.fetchall()

            result = []

            # 2️⃣ 각 리뷰에 username 추가
            for review in reviews:
                cursor.execute("SELECT username FROM users WHERE id = %s", (review['user_id'],))
                user = cursor.fetchone()
                username = user['username'] if user else "Unknown"

                # 3️⃣ 원하는 형태로 딕셔너리 구성
                result.append({
                    "username": username,
                    "rating": review['rating'],
                    "comment": review['comment']
                })

        return result

    except Exception as e:
        print(f"Error fetching product reviews: {e}")
        return []