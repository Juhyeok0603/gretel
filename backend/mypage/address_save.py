from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi import Request
import json
import base64
import requests



router = APIRouter()
load_dotenv() # .env 파일 로드


DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # 포트는 정수형으로 변환

TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY")

# DB 연결............
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

@router.post("/mypage/address_save", response_class=JSONResponse)
async def address_save(request: Request):
    try:
        userid= request.session.get("user_id")
        if not userid:
            return {"message":"로그인 후 이용 가능한 서비스입니다."}
        data = await request.json()
        print(data["postcode"])
        postcode = data["postcode"] # 우편번호
        address= data["address"] # 주소
        address_detail = data["detail"] # 상세 주소(동, 호수 등)
        print(postcode, address, address_detail)
        connection = get_db_con()
        with connection.cursor() as cursor:
            sql = "UPDATE users SET postcode=%s,address=%s, address_detail=%s WHERE id=%s"
            cursor.execute(sql, (postcode, address, address_detail, userid))
            connection.commit()
            connection.close()
        return {"message":"주소가 저장되었습니다."}
    except Exception as e:
        print(f"Error: {e}")
        return {"message": f"주소 저장 중 오류가 발생했습니다: {e}"}