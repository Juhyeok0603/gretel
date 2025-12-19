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

@router.get("/cart", response_class=HTMLResponse)
async def cart(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        print(user_id)
        connection = get_db_con()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM cart WHERE user_id = %s"
            cursor.execute(sql,(user_id))
            user_cart = cursor.fetchall()
            print(user_cart)
        return templates.TemplateResponse("cart.html",{"request":request, "message": user_id, "cart":user_cart})
    else:
        answer= "로그인이 필요합니다."
        return templates.TemplateResponse("cart.html",{"request": request, "message": 1})