from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from fastapi.responses import HTMLResponse
from fastapi import Request
import requests

router = APIRouter()
load_dotenv() # .env 파일 로드


# 도메인
DOMAIN=os.getenv("DOMAIN")

# 카카오 로그인 env
KAKAO_REST_API_KEY=os.getenv("KAKAO_REST_API_KEY")
KAKAO_CLIENT_SECRET=os.getenv("KAKAO_CLIENT_SECRET")
kauth_host="https://kauth.kakao.com"
kapi_host="https://kapi.kakao.com"
redirect_uri=DOMAIN+"/login/kakao/redirect"

@router.get("/unlink")
async def unlink(request: Request):
    try:
        headers = {'Authorization': f'Bearer {request.session.get("access_token")}'}
        res = requests.post(kapi_host+"/v1/user/unlink", headers=headers)
        print("Kakao unlink response:", res.json())
        request.session.clear()  # 세션 데이터 삭제
        return HTMLResponse(content="<script>window.location.href = './';</script>")
    except Exception as e:
        print(f"Error during unlink: {e}")
        return HTMLResponse(content="<script>alert('회원탈퇴 실패'); window.location.href = './';</script>")