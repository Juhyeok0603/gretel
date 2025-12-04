from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi import Request
import json
import base64
import requests
from fastapi.templating import Jinja2Templates

router = APIRouter()
load_dotenv() # .env 파일 로드

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY")


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

@router.get("/seller/brand",response_class=HTMLResponse)
async def seller_brand(request:Request):
    seller = request.session.get("seller")
    seller_id = request.session.get("seller_id")
    print("seller_id:",seller_id, "seller:",seller)
    if not seller:
        return HTMLResponse("<script>alert('로그인 후 이용 가능한 서비스입니다.'); window.location.href='/seller/seller_login';</script>")
    # 판매자 페이지에 bills 정보 가져오기
    connection = get_db_con()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM bills WHERE seller_id=%s"
        cursor.execute(sql, (seller_id,))
        bills = cursor.fetchall()
        print("bills:", bills)
    return templates.TemplateResponse("seller/brand.html",{"request":request, "seller":seller, "seller_id":seller_id,"bills": bills})
