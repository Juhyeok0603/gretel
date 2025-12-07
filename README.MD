# users - 사용자
#users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,       -- 사용자 고유 ID
    username VARCHAR(50) NOT NULL UNIQUE,    -- 로그인용 사용자 이름
    email VARCHAR(100) NOT NULL UNIQUE,      -- 이메일
    password VARCHAR(255) NOT NULL,     -- 비밀번호
    role ENUM('user','admin','seller') DEFAULT 'user', -- 사용자 역할
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,     -- 생성 시각
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP -- 마지막 수정 시각
);
# 이메일 인증용으로 users에 컬럼 추가
ALTER TABLE users
ADD COLUMN is_active BOOLEAN DEFAULT FALSE COMMENT '이메일 인증 완료 여부',
ADD COLUMN verification_token VARCHAR(255) COMMENT '이메일 인증 토큰';

# 카카오 저장용
ALTER TABLE users
ADD COLUMN access_token VARCHAR(255) NULL,
ADD COLUMN kakao_id bigint NULL UNIQUE;

# 주소 추가
ALTER TABLE users
ADD COLUMN postcode VARCHAR(10) DEFAULT NULL COMMENT '우편번호',
ADD COLUMN address VARCHAR(255) DEFAULT NULL COMMENT '기본 주소',
ADD COLUMN address_detail VARCHAR(255) DEFAULT NULL COMMENT '상세 주소';




# 상품 관련 테이블 설계
-- 1. products - 상품 기본 정보
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '상품 고유 ID',
    seller_id INT NOT NULL COMMENT '판매자 ID (users.id 참조)',
    name VARCHAR(100) NOT NULL COMMENT '상품 이름',
    price DECIMAL(10,2) NOT NULL COMMENT '상품 가격',
    stock INT DEFAULT 0 COMMENT '기본 재고 수량',
    categories JSON COMMENT '카테고리 목록 (예: ["남자","상의","겨울"])',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '상품 등록 시각',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '상품 정보 수정 시각',
    FOREIGN KEY (seller_id) REFERENCES users(id)
) COMMENT='상품 기본 정보 테이블 (멀티 카테고리 구조)';


-- 2. product_images - 대표 이미지
CREATE TABLE product_images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '이미지 고유 ID',
    product_id INT NOT NULL COMMENT '상품 ID (products.id 참조)',
    image_url VARCHAR(255) NOT NULL COMMENT '대표 이미지 URL',
    sort_order INT DEFAULT 0 COMMENT '이미지 순서 (1=대표 이미지)',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) COMMENT='상품 썸네일/대표 이미지 테이블';


-- 3. product_detail_img - 상세 이미지
CREATE TABLE product_detail_img (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '상세 이미지 고유 ID',
    product_id INT NOT NULL COMMENT '상품 ID (products.id 참조)',
    image_url VARCHAR(255) NOT NULL COMMENT '상세 이미지 URL',
    sort_order INT DEFAULT 0 COMMENT '상세 이미지 순서 (1부터)',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) COMMENT='상품 상세 이미지 테이블 (상세 설명용)';


-- 4. product_reviews - 리뷰
CREATE TABLE product_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '리뷰 고유 ID',
    product_id INT NOT NULL COMMENT '상품 ID (products.id 참조)',
    user_id INT NOT NULL COMMENT '리뷰 작성자 ID (users.id 참조)',
    rating TINYINT NOT NULL COMMENT '평점 (1~5)',
    comment TEXT COMMENT '리뷰 내용',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '리뷰 작성 시각',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT='상품 리뷰 테이블';


# cart - 장바구니
CREATE TABLE cart (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    size VARCHAR(10) NOT NULL,
    quantity INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_cart_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);


ALTER TABLE cart
ADD COLUMN price float NOT NULL DEFAULT 0 AFTER quantity;

# seller - 판매자
CREATE TABLE sellers (
    id INT NOT_NULL AUTO_INCREMENT PRIMARY KEY,                          -- 판매자 고유 ID
    brand_name VARCHAR(100) NOT NULL,               -- 브랜드명
    business_number VARCHAR(20) NOT NULL UNIQUE,    -- 사업자등록번호
    representative_name VARCHAR(50) NOT NULL,       -- 대표자 이름
    address VARCHAR(255) NOT NULL,                  -- 기본 주소
    address_detail VARCHAR(255),                    -- 상세 주소
    phone VARCHAR(20) NOT NULL,                     -- 전화번호
    email VARCHAR(100) NOT NULL UNIQUE,             -- 이메일
    bank_name VARCHAR(50) NOT NULL,                 -- 은행명
    account_number VARCHAR(50) NOT NULL,            -- 계좌번호
    account_holder VARCHAR(50) NOT NULL,            -- 예금주
    business_license_path VARCHAR(255),             -- 사업자등록증 파일 경로 (선택)
    bankbook_path VARCHAR(255),                     -- 통장사본 파일 경로 (선택)
    status VARCHAR(20) DEFAULT 'pending',           -- 상태 (대기중, 승인됨, 반려됨)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- 등록일시
);

# 빌즈 - 결제 정보
CREATE TABLE bills (
    id BIGSERIAL PRIMARY KEY,              -- 주문 고유 ID
    user_id BIGINT NOT NULL,               -- 주문한 사용자 ID
    seller_id BIGINT NOT NULL,             -- 판매자 ID
    product_id BIGINT NOT NULL,         -- 상품 ID 배열
    quantity INT NOT NULL,             -- 각 상품 수량 배열
    total_amount DECIMAL(10,2) NOT NULL,   -- 총 결제 금액
    status VARCHAR(20) DEFAULT 'pending',  -- 주문 상태
    payment_method VARCHAR(20),            -- 결제 수단
    postcode VARCHAR(10),                  -- 배송 우편번호
    address VARCHAR(255),                  -- 배송 주소
    address_detail VARCHAR(255),           -- 상세 주소
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);