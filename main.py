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
from backend.products import router as products_router
from backend.product_review import router as product_review_router
from backend.product_size import router as product_size_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# static 라우트
app.mount("/static", StaticFiles(directory="static"), name="static")

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

from backend.products import products_info
from backend.product_review import product_reviews
from backend.product_size import product_sizes
@app.get("/product/{product_id}", response_class=HTMLResponse)
async def products(request: Request, product_id: int):
    print(product_id)
    result = products_info(product_id)
    print("this is ",result)
    print(result['images_url'][0])
    review = product_reviews(product_id)
    print("reviews:", review)
    print("reviwer1:", review[0]['username'])
    sizes = product_sizes(product_id)
    print("sizes:", sizes)
    return templates.TemplateResponse("product_detail.html", {"request": request, "product": result, "review": review, "sizes": sizes})

#라우터 등록
app.include_router(sign_up_router)
app.include_router(login_router)
app.include_router(unlink_router)
app.include_router(products_router)
app.include_router(product_review_router)
app.include_router(product_size_router)
