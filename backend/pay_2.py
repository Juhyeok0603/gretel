from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import Request
import json
import requests



router = APIRouter()
load_dotenv() # .env 파일 로드


DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # 포트는 정수형으로 변환

# DB 연결
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



KAKAO_DEV_SECRET = os.getenv("KAKAO_SECRET_KEY")
KAKAOPAY_HOST = "https://open-api.kakaopay.com"

DOMAIN = os.getenv("DOMAIN")  # http://localhost:8000
APPROVAL_URL = f"{DOMAIN}/payment/approve"
CANCEL_URL = f"{DOMAIN}/payment/cancel"
FAIL_URL = f"{DOMAIN}/payment/fail"

@router.post("/payment/ready",response_class=JSONResponse)
async def payment_ready(request: Request):
    data = await request.json()
    #print(data)
    print(KAKAO_DEV_SECRET)
    print(DOMAIN)
    # 여기에 결제 준비 로직 추가
    try:
        user_id = str(data.get("user_id"))
        user = data.get("user")
        product_id = str(data.get("product_id"))
        quantity = int(data.get("quantity"))
        size = str(data.get("size"))
        price = int(data.get("price"))
        url = f"{KAKAOPAY_HOST}/online/v1/payment/ready"
        print("user_id:", user_id, "product_id:", product_id, "quantity:", quantity, "size:", size, "price:", price)
        headers = {     
            "Authorization": f"SECRET_KEY {KAKAO_DEV_SECRET}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        params = {
            "cid": "TC0ONETIME",
            "partner_order_id": "order_1234",
            "partner_user_id": user_id,
            "item_name": f"Product {product_id} Size {size}",
            "quantity": quantity,
            "total_amount": price,
            "tax_free_amount": 0,
            "approval_url": APPROVAL_URL,
            "cancel_url": CANCEL_URL,
            "fail_url": FAIL_URL
        }
        print("카카오 요청 params:", params)
        response = requests.post(url, headers=headers, data=params)
        print("리스폰스:", response.headers)
        print("응답 코드:", response.status_code)
        print("응답 내용:", response.text)
        return {"message": "결제 준비 완료"}
    except Exception as e:
        print(f"Error in payment ready: {e}")
        return {"message": "결제 준비 실패"}

@router.post("/payment/approve")
async def payment_approve(request: Request):
    data = await request.json()
    print("결제 승인 데이터:", data)
    # 여기에 결제 승인 로직 추가
    url = f"{KAKAOPAY_HOST}/online/v1/payment/approve"
    headers = {
        "Authorization": f"DEV_SECRET_KEY {KAKAO_DEV_SECRET}",
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    params = {
        "cid": "TC0ONETIME",
        "tid": data.get("tid"),
        "partner_order_id": "order1234",
        "partner_user_id": str(data.get("user_id")),
        "pg_token": data.get("pg_token")
    }
    response = requests.post(url, headers=headers, data=params)
    print("응답 코드:", response.status_code)
    return {"message": "결제 승인 완료"}
@router.post("/payment/cancel")
async def payment_cancel(request: Request):
    data = await request.json()
    print("결제 취소 데이터:", data)
    # 여기에 결제 취소 로직 추가
    return {"message": "결제 취소 완료"}
@router.post("/payment/fail")
async def payment_fail(request: Request):
    data = await request.json()
    print("결제 실패 데이터:", data)
    # 여기에 결제 실패 로직 추가
    return {"message": "결제 실패 처리 완료"}