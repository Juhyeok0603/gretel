from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from fastapi.responses import HTMLResponse
from fastapi import Request
import json


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

@router.post("/cart/add")
async def add_cart(request:Request):
    data = await request.json()
    product_id = data.get("product_id")
    quantity = data.get("quantity")
    user_id = data.get("user_id")
    size = data.get("size")
    price = data.get("price")
    print(f"Adding to cart: user_id={user_id}, product_id={product_id}, quantity={quantity}, size={size}, price={price}")
    if not user_id:
        return HTMLResponse("로그인이 필요합니다.", status_code=401)
    try:
        connection = get_db_con()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM cart WHERE product_id = %s AND user_id = %s"
            cursor.execute(sql, (product_id, user_id))
            existing_item = cursor.fetchone()
            if existing_item:
                sql = "UPDATE cart SET quantity = %s, size = %s, price = %s WHERE product_id = %s AND user_id = %s"
                cursor.execute(sql, (quantity, size, price, product_id, user_id))
                connection.commit()
                return {"success": True, "message": "장바구니 내용이 업데이트되었습니다."}
            else:
                sql = "INSERT INTO cart (user_id, product_id, quantity, size, price) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (user_id, product_id, quantity, size, price))
                connection.commit()
                return {"success": True, "message": "장바구니에 추가되었습니다."}
    except Exception as e:
        print(f"Error adding to cart: {e}")
        return HTMLResponse(content=json.dumps({"success": False, "message": "장바구니 추가에 실패했습니다."}), status_code=500)
    finally:
        connection.close()
