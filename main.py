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


# 상품 상세 페이지
@app.get("/products", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("products.html", {"request": request})

# 마이페이지 라우트는 mypage.py에서
from backend.mypage import get_user_name
@app.get("/mypage", response_class=HTMLResponse)
async def mypage(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        username = get_user_name(user_id)
    else:
        username= None
    print(username)
    return templates.TemplateResponse("mypage.html", {"request": request, "username": username})





#라우터 등록
app.include_router(sign_up_router)
app.include_router(login_router)
app.include_router(unlink_router)

# css 라우트

app.mount("/static", StaticFiles(directory="static"), name="static")