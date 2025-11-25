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


def index_page(request:Request):
    try:
        connection = get_db_con()
        cursor = connection.cursor()

        base_path = f"./static/images/products/"
        random_product= []
        # 상품 4개 랜덤 조회
        sql = "SELECT * FROM products ORDER BY RAND() LIMIT 4"
        cursor.execute(sql)
        products = cursor.fetchall()
        # 각 상품에 대표 이미지 추가
        for product in products:
            image_url = None
            product_id = product["id"]
            product_name = product.get("name")
            for ext in ['webp','jpg','jpeg','png']:
                path = os.path.join(base_path,f"{product_id}/1.{ext}")
                if os.path.exists(path):
                    image_url = f"./static/images/products/{product_id}/1.{ext}"
                    break
            if image_url:
                random_product.append({
                    'product_id': product_id,
                    'product_name':product_name,
                    'image_url':image_url,
                    'price':product.get('price')
                })
            else:
                random_product.append({
                    'product_id': product_id,
                    'product_name':product_name,
                    'image_url':f"./static/images/products/default.png",
                    'price':0
                })
        
        return random_product
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

    finally:
        connection.close()