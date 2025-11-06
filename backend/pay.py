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


@router.post("/payment/ready", response_class=JSONResponse)
async def payment_ready(request: Request):
    data = await request.json()
    # 여기에 결제 준비 로직 추가
    try:
        user_id = str(data.get("user_id"))
        user = data.get("user")
        product_id = str(data.get("product_id"))
        quantity = int(data.get("quantity"))
        size = str(data.get("size"))
        price = int(data.get("price"))
        url = "https://api.tosspayments.com/v1/payments"
        print("user_id:", user_id, "product_id:", product_id, "quantity:", quantity, "size:", size, "price:", price)
        encoded_secret = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {encoded_secret}",
            "Content-Type": "application/json"
        }
        params = {
            "amount": price,
            "orderId": user_id,
            "orderName": f"Product={product_id} x {quantity}",
            "customerName": user,
            "successUrl": f"{os.getenv('DOMAIN')}/payment/success",
            "failUrl": f"{os.getenv('DOMAIN')}/payment/fail",
            "cancelUrl": f"{os.getenv('DOMAIN')}/payment/cancel",
            "method": "CARD"
        }
        response = requests.post(url, headers=headers, json=params)
        result = response.json()
        checkout_url = result.get("checkout",{}).get("url")
        print("Checkout URL:", checkout_url)
        if checkout_url:
            return JSONResponse(content={"checkout_url": checkout_url}, status_code=200)
        return JSONResponse(content=result,status_code=response.status_code)
    except Exception as e:
        print("Error in payment_ready:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)