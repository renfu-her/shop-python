# DEMO 商場 (DEMO Mall E-commerce Platform)

一個基於 Flask MVC 架構的電商平台，支援多商店經營模式，提供完整的購物車、優惠券、訂單管理等功能。

## 功能特色

### 🛍️ 商城功能
- **商品瀏覽**：支援分類篩選、搜尋功能
- **購物車**：商品加入、數量調整、移除
- **結帳系統**：支援優惠券應用
- **訂單管理**：訂單追蹤、狀態更新

### 👥 會員系統
- **會員註冊/登入**：獨立的會員認證系統
- **個人資料管理**：個人資訊編輯
- **我的商店**：會員可創建多個商店
- **訂單歷史**：查看購買記錄

### 🏪 商店管理
- **商店創建**：會員可創建多個商店
- **商品管理**：商品 CRUD 操作
- **訂單處理**：商店訂單管理
- **優惠券管理**：商店專屬優惠券

### 👨‍💼 後台管理
- **管理員登入**：獨立的後台認證
- **商店審核**：啟用/停用商店
- **用戶管理**：管理員帳號管理
- **平台優惠券**：全站優惠券管理
- **訂單監控**：全站訂單查看

### 🎫 優惠券系統
- **多種折扣類型**：百分比折扣、固定金額折扣
- **使用限制**：最低消費、最大折扣、使用次數限制
- **適用範圍**：全站、特定商店、特定分類
- **有效期管理**：開始/結束時間設定

## 技術架構

### 後端技術
- **框架**：Flask 2.3.3
- **資料庫**：MySQL
- **ORM**：PyMySQL
- **認證**：Werkzeug Security
- **表單**：WTForms

### 前端技術
- **CSS 框架**：Bootstrap 5.3.0
- **圖標**：Font Awesome 6.0.0
- **JavaScript**：原生 JS + Bootstrap JS

### 資料庫設計
- **members**：會員資料
- **users**：管理員帳號
- **stores**：商店資料
- **categories**：商品分類
- **products**：商品資料
- **coupons**：優惠券
- **orders**：訂單
- **order_items**：訂單明細
- **cart**：購物車

## 安裝與設定

### 1. 環境需求
- Python 3.8+
- MySQL 5.7+
- Git

### 2. 安裝步驟

```bash
# 1. 克隆專案
git clone <repository-url>
cd street-foods

# 2. 創建虛擬環境
python -m venv venv

# 3. 啟動虛擬環境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 設定資料庫
# 確保 MySQL 服務運行，創建資料庫
mysql -u root -p
CREATE DATABASE `shop-data`;

# 6. 設定環境變數（可選）
# 創建 .env 檔案
echo "SECRET_KEY=your-secret-key-here" > .env

# 7. 運行應用
python run.py
```

### 3. 資料庫設定
- **主機**：localhost
- **用戶名**：root
- **密碼**：空（可修改 config.py）
- **資料庫**：shop-data

### 4. 預設帳號
- **管理員**：username: `admin`, password: `admin123`
- **會員**：需要註冊

## 使用說明

### 會員操作
1. **註冊會員**：訪問 `/member/register`
2. **創建商店**：登入後點擊「我的商店」→「創建新商店」
3. **管理商品**：進入商店後台管理商品
4. **購物**：瀏覽商品，加入購物車，結帳

### 管理員操作
1. **登入後台**：訪問 `/admin/login`
2. **審核商店**：在商店管理頁面啟用/停用商店
3. **管理優惠券**：創建全站優惠券
4. **監控訂單**：查看所有訂單狀態

### 商店經營
1. **商品上架**：添加商品資訊、價格、庫存
2. **訂單處理**：查看訂單，更新訂單狀態
3. **優惠券**：創建商店專屬優惠券
4. **數據統計**：查看銷售數據

## 專案結構

```
street-foods/
├── app/
│   ├── __init__.py              # Flask 應用工廠
│   ├── models/                  # 資料模型
│   │   ├── member.py           # 會員模型
│   │   ├── user.py             # 管理員模型
│   │   ├── store.py            # 商店模型
│   │   ├── product.py          # 商品模型
│   │   ├── category.py         # 分類模型
│   │   ├── coupon.py           # 優惠券模型
│   │   ├── order.py            # 訂單模型
│   │   └── cart.py             # 購物車模型
│   ├── controllers/             # 控制器
│   │   ├── member_controller.py    # 會員控制器
│   │   ├── admin_controller.py     # 管理員控制器
│   │   ├── store_controller.py     # 商店控制器
│   │   ├── product_controller.py   # 商品控制器
│   │   ├── cart_controller.py      # 購物車控制器
│   │   ├── order_controller.py     # 訂單控制器
│   │   └── coupon_controller.py    # 優惠券控制器
│   ├── views/                   # 視圖模板
│   │   ├── layout.html         # 基礎模板
│   │   ├── member/             # 會員頁面
│   │   ├── admin/              # 管理員頁面
│   │   ├── store/              # 商店頁面
│   │   ├── shop/               # 商城頁面
│   │   ├── cart/               # 購物車頁面
│   │   └── order/              # 訂單頁面
│   ├── static/                 # 靜態資源
│   │   ├── css/style.css       # 自定義樣式
│   │   ├── js/main.js          # 自定義腳本
│   │   └── images/             # 圖片資源
│   └── utils/                  # 工具函數
│       ├── db.py               # 資料庫連接
│       ├── auth.py             # 認證裝飾器
│       └── helpers.py          # 輔助函數
├── config.py                   # 配置文件
├── requirements.txt            # 依賴清單
├── run.py                      # 應用入口
└── README.md                   # 說明文檔
```

## 開發說明

### 添加新功能
1. 在 `models/` 中定義資料模型
2. 在 `controllers/` 中實現業務邏輯
3. 在 `views/` 中創建模板
4. 在 `__init__.py` 中註冊藍圖

### 資料庫遷移
- 修改 `app/utils/db.py` 中的 `init_db` 函數
- 重新運行應用會自動執行 SQL 語句

### 樣式自定義
- 修改 `app/static/css/style.css`
- 使用 Bootstrap 變數進行主題自定義

## 注意事項

1. **安全性**：生產環境請修改預設密碼和 SECRET_KEY
2. **圖片上傳**：確保 `app/static/images/products/` 目錄存在
3. **資料庫**：定期備份 MySQL 資料庫
4. **性能**：大量商品時考慮添加分頁和緩存

## 授權

此專案僅供學習使用，請勿用於商業用途。

## 聯絡資訊

如有問題或建議，請聯繫開發團隊。
