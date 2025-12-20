from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from fastapi.responses import HTMLResponse
from fastapi import Request
import json
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="templates")
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

# 이미지 불러오기 함수
import glob

def get_product_image(product_id: int):
    base_path = f"static/images/products/{product_id}/1.*"
    files = glob.glob(base_path)

    if files:
        # static 기준 경로로 변환
        return "/" + files[0].replace("\\", "/")
    else:
        return "../static/images/products/default.png"



@router.get("/cart", response_class=HTMLResponse)
async def cart(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return templates.TemplateResponse(
            "cart.html",
            {"request": request, "message": "로그인이 필요합니다."}
        )

    connection = get_db_con()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM cart WHERE user_id = %s", (user_id,))
        user_cart = cursor.fetchall()

        cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
        user_name = cursor.fetchone()["username"]

    # 🔥 여기서 이미지 경로 추가
    for item in user_cart:
        item["image_url"] = get_product_image(item["product_id"])

    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "message": user_name,
            "cart": user_cart
        }
    )
