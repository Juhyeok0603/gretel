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

# 바로구매 로직
@router.post("/payment/ready", response_class=JSONResponse)
async def payment_ready(request: Request):
    session_user = request.session.get("user_id")
    if not session_user:
        return JSONResponse(content={"error":"로그인이 필요합니다"}, status_code=401)
    print("Session User Id:", session_user)
    connection = get_db_con()
    data = await request.json()
    user_id = str(data.get("user_id"))
    user = data.get("user")
    product_id = str(data.get("product_id"))
    quantity = int(data.get("quantity"))
    product_name = str(data.get("product_name"))
    size = str(data.get("size"))
    price = int(data.get("price"))
        # 배송지(주소) 없으면 에러
    with connection.cursor() as cursor:
        sql = "SELECT postcode, address, address_detail FROM users WHERE id =%s"
        cursor.execute(sql, (user_id,))
        address_info = cursor.fetchone()
        print(address_info)
        if not address_info["postcode"] or not address_info["address_detail"] or not address_info["address"]:
            return JSONResponse(content={"message": "배송지 주소를 등록해주세요."}, status_code=400)
    # 여기에 결제 준비 로직 추가
    try:
            
        # 결제 요청
        url = "https://api.tosspayments.com/v1/payments"
        print("user_id:", user_id, "product_id:", product_id, "quantity:", quantity, "size:", size, "price:", price)
        encoded_secret = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {encoded_secret}",
            "Content-Type": "application/json"
        }
        params = {
            "amount": price,
            "orderId": user_id, #주문자
            "orderName": product_id, #주문상품
            "customerName": user,
            "successUrl": f"{os.getenv('DOMAIN')}/payment/success",
            "failUrl": f"{os.getenv('DOMAIN')}/payment/fail",
            "cancelUrl": f"{os.getenv('DOMAIN')}/payment/cancel",
            "method": "CARD"
        }
        response = requests.post(url, headers=headers, json=params)
        result = response.json()
        print("Toss Payments Response:", result)
        checkout_url = result.get("checkout",{}).get("url")
        print("Checkout URL:", checkout_url)
        if checkout_url:
            return JSONResponse(content={"checkout_url": checkout_url}, status_code=200)
        return JSONResponse(content=result,status_code=response.status_code)
    except Exception as e:
        print("Error in payment_ready:", str(e))
        return JSONResponse(content={"message": "결제 준비 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요"}, status_code=500)