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

# 카카오 로그인 env
KAKAO_REST_API_KEY=os.getenv("KAKAO_REST_API_KEY")
KAKAO_CLIENT_SECRET=os.getenv("KAKAO_CLIENT_SECRET")
# 카카오 인증 호스트
kauth_host="https://kauth.kakao.com"
# 카카오 API 호스트(사용자 정보, 로그아웃, 연결끊기 등)
kapi_host="https://kapi.kakao.com"
# 리다이렉트 경로
redirect_uri=DOMAIN+"/login/kakao/redirect"

# 로그인 성공 및 실패 메시지
login_success = "<script>alert('로그인성공'); window.location.href='./';</script>"
login_fail = "<script>alert('로그인 실패'); window.location.href='./login';</script>"

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
    ):
    print(f"email:{email}, password:{password}")
    try:
        sql = "SELECT * FROM users WHERE email=%s"
        connection = get_db_con()
        with connection.cursor() as cursor:
            cursor.execute(sql,(email))
            result = cursor.fetchone()
            if result is None:
                return HTMLResponse(
                    content=login_fail
                )
    except Exception as e:
        print(f"Error: {e}")
        return HTMLResponse( login_fail)
    try:
        pw_sql="SELECT id,username,password,id FROM users WHERE email=%s"
        connection = get_db_con()
        with connection.cursor() as cursor:
            cursor.execute(pw_sql, (email))
            result=cursor.fetchone()
            hashed_password=result['password']
            username = result['username']
            user_id = result['id']
            if bcrypt.verify(password, hashed_password):
                request.session['user']=username
                request.session['user_id']=user_id
                return templates.TemplateResponse("index.html", {"request": request, "message": "로그인 성공", "username": username})
            else:
                return HTMLResponse( content="<script>alert('로그인 실패'); window.location.href = './login';</script>")
    except Exception as e:
        print(f"Error: {e}")
        return HTMLResponse( content="<script>alert('로그인 실패'); window.location.href = '/login';</script>")


@router.get("/logout")
async def logout(request: Request):
    try:
        user_id=request.session.get("user_id")
        if not user_id:
            return HTMLResponse(content="<script>alert('로그아웃 실패: 사용자 정보 없음'); window.location.href = './';</script>")
        connection = get_db_con()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE id=%s", (user_id))
            result = cursor.fetchone()
            if result is None:
                return HTMLResponse(content="<script>alert('로그아웃 실패: 사용자 정보 없음'); window.location.href = './';</script>")
        access_token = result["access_token"]
        headers = {'Authorization': f'Bearer {access_token}'}
        res = requests.post(kapi_host+"/v1/user/logout", headers=headers)
        print("Kakao logout response:", res.json())
        request.session.clear()  # 세션 데이터 삭제
        response = RedirectResponse(url="/", status_code=303)
        return response
    except Exception as e:
        print(f"Error during logout: {e}")
        return HTMLResponse(content="<script>alert('로그아웃 실패'); window.location.href = './';</script>")

# 카카오 로그인 라우트
@router.get("/login/kakao")
async def kakao_login():
    kakao_login_url=f"{kauth_host}/oauth/authorize?response_type=code&client_id={KAKAO_REST_API_KEY}&redirect_uri={redirect_uri}"
    return RedirectResponse(kakao_login_url)

@router.get("/login/kakao/redirect")
async def kakao_login_redirect(request: Request, code: str):
    try:
        data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_REST_API_KEY,
            "client_secret": KAKAO_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "code":code
        }
        res = requests.post(f"{kauth_host}/oauth/token", data=data)
        token_json = res.json()
        access_token = token_json.get("access_token")
        if not access_token:
            return HTMLResponse(content=login_fail)
        headers={
            "Authorization": f"Bearer {access_token}"
        }
        res = requests.get(kapi_host+"/v2/user/me", headers=headers)
        profile_json = res.json()
        print(profile_json)
        print("kakao_id:", profile_json["id"])
        kakao_id = profile_json["id"]
        username = profile_json["kakao_account"]["profile"]["nickname"]
        connection = get_db_con()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE kakao_id=%s", (kakao_id,))
            result = cursor.fetchone()
            print("kakao_id:", kakao_id)
            print("dbresult:", result)
            if result is None:
                try:
                    cursor.execute("INSERT INTO users (username, kakao_id, access_token) VALUES (%s, %s, %s)", (username, kakao_id, access_token))
                    user_id = cursor.lastrowid
                    print(user_id)
                    request.session["user_id"] = user_id
                    request.session["user"] = username
                    connection.commit()
                    print(f"{username}이 카카오로 회원가입")
                except Exception as e:
                    print(f"Error: {e}")
                    connection.rollback()
            else:
                user_id = result['id']
                request.session["user_id"] = user_id
                print(f"{username}이 카카오로 로그인")
                request.session["user"] = username
            return RedirectResponse("/")
    except Exception as e:
        print(f"Error during Kakao login: {e}")
        return HTMLResponse(content=login_fail)
