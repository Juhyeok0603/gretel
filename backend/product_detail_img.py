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

def products_detail_img(product_id: int):
    try:
        base_path = f"./static/images/product_detail/{product_id}"
        detail_img = []
        i = 1
        while True:
            found = False  # i번째 이미지가 존재하는지 체크
            for ext in ['webp', 'jpg', 'jpeg', 'png']:
                path = os.path.join(base_path, f"{i}.{ext}")
                if os.path.exists(path):
                    detail_img.append({
                        'product_id': product_id,
                        'image_url': f"/images/product_detail/{product_id}/{i}.{ext}"
                    })
                    found = True  # 최소 하나 발견
            if not found:
                break  # i번째 번호에 이미지가 하나도 없으면 종료
            i += 1

        return detail_img
    except Exception as e:
        print(f"Error: {e}")
        return HTMLResponse(f"Error: {e}")