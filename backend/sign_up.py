from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from passlib.hash import bcrypt
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates


# 이메일 인증용
import secrets
import smtplib
from email.mime.text import MIMEText

router = APIRouter()
load_dotenv() # .env 파일 로드

# 템플릿 설정
templates = Jinja2Templates(directory="templates")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # 포트는 정수형으로 변환

# DB 연결
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT,
    charset='utf8mb4', # 문자 인코딩-유니코드를 안전하게 저장 가능
    cursorclass=pymysql.cursors.DictCursor # 결과를 딕셔너리 형태로 반환
)
cursor = connection.cursor()


@router.post("/sign_up")
async def users(request:Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
    ):
    print(f"Received user: {username, email, password}")  # 터미널에 출력

    if not username or not email or not password:
        return templates.TemplateResponse("sign_up.html", {"request": request, "error": "모든 항목을 채워주세요"})

    # 비밀번호 해싱
    password_hash = bcrypt.hash(password)
    print(f"hash_password:{password_hash}")
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password_hash))
        connection.commit()
        print(f"{username}이 회원가입")
        cursor.close()
        connection.close()
        return HTMLResponse( content="<script>alert('회원가입 성공'); window.location.href = '/login';</script>")
        
    except Exception as e:
        print(f"Error: {e}")
        connection.rollback()
        cursor.close()
        connection.close()
        return HTMLResponse( content="<script>alert('회원가입 실패'); window.location.href = '/sign_up';</script>")

    