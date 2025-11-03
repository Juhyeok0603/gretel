from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from passlib.hash import bcrypt
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates


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



def products_info(product_id: int):
    print(product_id)
    try:
        you_want = "products"
        sql = f"SELECT * FROM {you_want} WHERE product_id= %s"
        connection = get_db_con()
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {you_want} WHERE id= %s",(product_id)) # products
            result = cursor.fetchone()
            print(type(result))
            print(result)
            name = result['name']
            description = result['description']
            price = result['price']
            category =result['category']
            seller_id = result['seller_id']
        with connection.cursor() as cursor:
            you_want = "product_images"
            sql = f"SELECT * FROM {you_want} WHERE product_id= %s ORDER BY sort_order" # product_images
            cursor.execute(sql,(product_id))
            images = cursor.fetchall()
            if not images:
                return {"message": "이미지 없음"}
            images_url= [img["image_url"] for img in images]
            print(images_url)
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM product_details WHERE product_id = %s"
            cursor.execute(sql,(product_id))
            details=cursor.fetchone()
            if not details:
                return {"message":"세부사항 없음"}
            print(details)
            material=details['material']
            origin=details['origin']
            model_info=details['model_info']
        return {
            "name":name,
            "description":description,
            "price": price,
            "category":category,
            "seller_id":seller_id,
            "material":material,
            "origin":origin,
            "model_info":model_info,
            "images_url": images_url,

            }
    except Exception as e:
        print(f"Error: {e}")
        return HTMLResponse(f"Error: {e}")