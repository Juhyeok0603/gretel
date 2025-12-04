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

TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY")


DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))  # 포트는 정수형으로 변환

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

@router.get("/payment/success", response_class=HTMLResponse)
async def payment_success(request: Request):
    try:
        paymentKey = request.query_params.get("paymentKey")
        orderId = request.query_params.get("orderId")

        print("paymentKey:", paymentKey)
        print("orderId:", orderId)
        url = f"https://api.tosspayments.com/v1/payments/{paymentKey}"

        encoded_secret = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode("utf-8")).decode("utf-8")
        headers = {
            "Authorization": f"Basic {encoded_secret}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        result = response.json()
        print("조회결과:",result)
        orderId = result.get("orderId") # 주문자 ID
        orderName = result.get("orderName") # 상품 ID
        amount = result.get("totalAmount") # 결제 금액
        print("주문자ID:", orderId, "상품ID:", orderName, "총액:", amount)
        #DB연결
        connection = get_db_con()
        with connection.cursor() as cursor:
            # 결제 정보 불러오기 - 수량 계산용
            sql = "select price from products where id=%s"
            cursor.execute(sql,(orderName))
            price = cursor.fetchone()
            price =int(price['price'])
            print("price:", price)
            quantity = amount / price
            print("quantity:", quantity)
            # 결제 정보 불러오기 - 주문자
            sql = "SELECT * FROM users WHERE id=%s"
            cursor.execute(sql,(orderId))
            order_user = cursor.fetchone()
            print("order_user:", order_user["username"])
            # 현재 사용자와 결제자가 맞는지 확인
            session_user = request.session.get("user")
            print("session_user:", session_user)
            # 판매자 정보 불러오기
            sql = "SELECT seller_id from products WHERE id=%s"
            cursor.execute(sql,(orderName))
            seller = cursor.fetchone()
            seller = seller['seller_id']
            print("seller:", seller)
            #주소 추가
            sql = "SELECT * FROM users WHERE id=%s"
            cursor.execute(sql,(orderId,))
    

            # 빌즈 내용
            bills = {
                "user_id": orderId,
                "product_id": orderName,
                "quantity": quantity,
                "total_amount": amount,
                "seller_id": seller
            }
            
            # 빌즈 작성 -> bills 테이블 삽입
            sql = "INSERT INTO bills (user_id, product_id,seller_id, quantity, total_amount) VALUES(%s, %s, %s, %s, %s)"
            cursor.execute(sql,(orderId, orderName, seller, quantity, amount))
            connection.commit()
            connection.close()
        return HTMLResponse(content="<script>alert('결제가 완료되었습니다.'); window.location.href='/';</script>", status_code=200)
    except Exception as e:
        print("Error: ",e)
        return HTMLResponse(content="오류", status_code=400)