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
from backend.cart import router as cart_router
from backend.pay import router as pay_router

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
    user= request.session.get("user")
    user_id = request.session.get("user_id")
    print("user_id:", user_id, "user:", user)
    return templates.TemplateResponse("index.html", {"request": request})
@app.get("/sign_up", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})
@app.get("/login", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})
@app.get("/payment/success", response_class=HTMLResponse)
async def payment_success(request: Request):
    return templates.TemplateResponse("payment/success.html", {"request": request})
@app.get("/payment/fail", response_class=HTMLResponse)
async def payment_fail(request: Request):
    return templates.TemplateResponse("payment/fail.html", {"request": request})
@app.get("/payment/cancel", response_class=HTMLResponse)
async def payment_cancel(request: Request):
    return templates.TemplateResponse("payment/cancel.html", {"request": request})

# 상품 상세 페이지
@app.get("/products", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("product_detail.html", {"request": request})

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


from backend.products import  products_info
from backend.product_images import products_images
from backend.product_detail_img import products_detail_img
from backend.product_review import product_reviews
@app.get("/product/{product_id}", response_class=HTMLResponse)
async def products(request: Request, product_id: int):
    product = products_info(product_id)
    if not product:
        return HTMLResponse(content="Product not found", status_code=404)
    images = products_images(product_id)
    if not images:
        images = []
    print("images:", images)
    detail_images = products_detail_img(product_id)
    if not detail_images:
        detail_images = []
    review = product_reviews(product_id)
    user = request.session.get("user")
    user_id = request.session.get("user_id")
    print("product:", product, "images:", images, "detail_images:", detail_images, "review:", review)
    return templates.TemplateResponse("product_detail.html", {"request": request, "product_id": product_id, "product": product, "images": images, "detail_images": detail_images, "review": review, "user": user, "user_id": user_id})

#라우터 등록
app.include_router(sign_up_router)
app.include_router(login_router)
app.include_router(unlink_router)
app.include_router(cart_router)
app.include_router(pay_router)