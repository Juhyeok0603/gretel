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
from backend.cart.cart_add import router as cart_add_router
from backend.pay import router as pay_router

# cart
from backend.cart.cart import router as cart_router

#결제
from backend.pay_success import router as pay_success_router

# seller/seller_regist
from backend.seller.seller_regist import router as seller_regist_router
from backend.seller.seller_login import router as seller_login_router


app = FastAPI()
templates = Jinja2Templates(directory="templates")

# static 라우트
app.mount("/static", StaticFiles(directory="static"), name="static")

# 세션 미들웨어 설정
from starlette.middleware.sessions import SessionMiddleware
secret = os.getenv("SECRET_KEY")
app.add_middleware(
    SessionMiddleware, 
    secret_key=secret,
    max_age=None
    )

# html 페이지 라우트
from backend.index import index_page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user= request.session.get("user")
    user_id = request.session.get("user_id")
    print("user_id:", user_id, "user:", user)
    print("-----------------------")
    random_products = index_page(request)
    print(random_products)
    return templates.TemplateResponse("index.html", {"request": request, "product":random_products})
@app.get("/sign_up", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})
@app.get("/login", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

#결제 이후 라우트
app.include_router(pay_success_router)

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
from backend.mypage.mypage import get_user_name
@app.get("/mypage", response_class=HTMLResponse)
async def mypage(request: Request):
    user_id = request.session.get("user_id")
    if user_id:
        username = get_user_name(user_id)
    else:
        username= None
    print(username)
    return templates.TemplateResponse("/mypage/mypage.html", {"request": request, "username": username})
@app.get("/address", response_class=HTMLResponse)
async def address(request: Request):
    return templates.TemplateResponse("/mypage/address.html",{"request": request})
# 마이페이지 - 주소 저장 라우트
from backend.mypage.address_save import router as address_save_router
app.include_router(address_save_router)


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



# 판매자 페이지
@app.get("/seller/seller_regist", response_class=HTMLResponse)
async def seller_regist(request:Request):
    return templates.TemplateResponse("seller/seller_regist.html",{"request":request})
@app.get("/seller/sellers", response_class=HTMLResponse)
async def seller_regist(request:Request):
    return templates.TemplateResponse("seller/sellers.html",{"request":request})
@app.get("/seller/product_regist", response_class=HTMLResponse)
async def seller_regist(request:Request):
    return templates.TemplateResponse("seller/product_regist.html",{"request":request})
@app.get("/seller/seller_login",response_class=HTMLResponse)
async def seller_login(request:Request):
    return templates.TemplateResponse("seller/seller_login.html",{"request":request})
from backend.seller.brand.mybrand import router as seller_brand_router
app.include_router(seller_brand_router) # 판매자 페이지 라우트



#라우터 등록
app.include_router(sign_up_router)
app.include_router(login_router)
app.include_router(unlink_router)
app.include_router(cart_add_router)
app.include_router(pay_router)
app.include_router(cart_router)
app.include_router(seller_regist_router)
app.include_router(seller_login_router)