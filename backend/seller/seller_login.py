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

# 도메인
DOMAIN=os.getenv("DOMAIN")

@router.post("/seller/seller_login")
async def seller_login(
    request:Request,
    email: str = Form(...),
    business_number: str = Form(...)
):
    print("Seller_Email:", email, "BusinessNumber:", business_number)
    connection = get_db_con()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM sellers WHERE email = %s AND business_number= %s"
            cursor.execute(sql, (email, business_number))
            result = cursor.fetchone()
            if result:
                request.session["seller"] = result["brand_name"]
                request.session["seller_id"]= result["id"]
                print("seller_id:",request.session.get("seller_id"))
                return RedirectResponse(url="/seller/brand", status_code=303, )
            else:
                return HTMLResponse("<script>alert('로그인 실패: 이메일 또는 사업자 번호가 올바르지 않습니다'); window.location.href='/seller/login';</script>")
    except Exception as e:
        print(f"Error: {e}")
        return HTMLResponse("<script>alert('로그인 오류 발생. 다시 시도해주세요.'); window.location.href='/seller/login';</script>")