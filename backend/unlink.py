from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from fastapi.responses import HTMLResponse
from fastapi import Request
import requests

router = APIRouter()
load_dotenv() # .env 파일 로드


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

# 도메인
DOMAIN=os.getenv("DOMAIN")

# 카카오 로그인 env
KAKAO_REST_API_KEY=os.getenv("KAKAO_REST_API_KEY")
KAKAO_CLIENT_SECRET=os.getenv("KAKAO_CLIENT_SECRET")
# 카카오 인증 호스트
kauth_host="https://kauth.kakao.com"
# 카카오 API 호스트(사용자 정보, 로그아웃, 연결끊기 등)
kapi_host="https://kapi.kakao.com"
redirect_uri=DOMAIN+"/login/kakao/redirect"

@router.get("/unlink")
async def unlink(request: Request):
    try:
        user_id = request.session.get("user_id")
        if user_id:
            cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            result = cursor.fetchone()
            if result is None:
                print(f"No user found with ID {user_id}")
                return HTMLResponse(content="<script>alert('회원탈퇴 실패: 사용자 정보 없음'); window.location.href = './';</script>")
            access_token = result['access_token']
            cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
            connection.commit()
            if access_token:
                print(f"Access token found for user ID {user_id}, proceeding to unlink from Kakao.")
                headers = {'Authorization': f'Bearer {access_token}'}
                res = requests.post(kapi_host+"/v1/user/unlink", headers=headers)
                print("Kakao unlink response:", res.json())
            print(f"User with ID {user_id} has been deleted from the database.")
            request.session.clear()  # 세션 데이터 삭제
            return HTMLResponse(content="<script>window.location.href = './';</script>")
        else:
            print("No user_id found in session.")
            return HTMLResponse(content="<script>alert('회원탈퇴 실패: 사용자 정보 없음'); window.location.href = './';</script>")
    except Exception as e:
        print(f"Error during unlink: {e}")
        return HTMLResponse(content="<script>alert('회원탈퇴 실패'); window.location.href = './';</script>")