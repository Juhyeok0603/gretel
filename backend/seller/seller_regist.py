from fastapi import APIRouter, Form
import pymysql
from dotenv import load_dotenv
import os
from fastapi.responses import HTMLResponse
from fastapi import Request
import json
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="templates")
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

@router.post("/seller/seller_regist")
async def seller_regist(request:Request):
    data=await request.json()
    brandName = data.get("brandName")
    businessNumber=data.get("businessNumber")
    representativeName=data.get("representativeName")
    address=data.get("address")
    addressDetail=data.get("addressDetail")
    phone=data.get("phone")
    email=data.get("email")
    bankName=data.get("bankName")
    accountNumber = data.get("accountNumber") #추후 암호화.
    accountHolder=data.get("accountHolder")
    connection = get_db_con()
    with connection.cursor() as cursor:
        try:        
            cursor.execute("INSERT INTO sellers(brand_name, business_number,representative_name, address, address_detail, phone, email, bank_name, account_number, account_holder) VALUES(%s, %s, %s, %s, %s, %s,%s,%s,%s,%s )",(brandName, businessNumber, representativeName, address, addressDetail, phone, email, bankName, accountNumber, accountHolder))
            connection.commit()
            cursor.close()
            connection.close()
            return {"message":"신청이 완료 되었습니다. 검토 후 자동으로 등록됩니다."}
        except Exception as e:
            print(f"Error: {e}")
            connection.rollback()
            cursor.close
            connection.close()
            return{"message":"신청이 불가합니다. 자세한 사항은 고객센터에 문의해주세요."}
