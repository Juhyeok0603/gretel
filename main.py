from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv

# static 파일 설정
from fastapi.staticfiles import StaticFiles

#라우터 등록
from backend.sign_up import router as sign_up_router
from backend.login import router as login_router
from backend.unlink import router as unlink_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 세션 미들웨어 설정
from starlette.middleware.sessions import SessionMiddleware
secret = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=secret)

# html 페이지 라우트
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/sign_up", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})
@app.get("/login", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
@app.get("/mypage", response_class=HTMLResponse)
async def mypage(request: Request):
    if not request.session.get("user"):
        return HTMLResponse( content="<script>alert('로그인 후 이용해주세요'); window.location.href = '/';</script>")
    return templates.TemplateResponse("mypage.html", {"request": request, "username": request.session.get("user")})





#라우터 등록
app.include_router(sign_up_router)
app.include_router(login_router)
app.include_router(unlink_router)

# css 라우트

app.mount("/static", StaticFiles(directory="static"), name="static")