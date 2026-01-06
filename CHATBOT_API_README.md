# 企業導入 AI 助理 Chatbot API 文檔

## 概述

這是一個完整的聊天機器人API系統，用於協助使用者通過對話方式輸入公司和產品資訊。系統具有以下特點：

- ✅ **對話式資料收集**：透過自然對話引導使用者輸入資料
- ✅ **會話記憶**：每個使用者擁有獨立的聊天會話，確保資料隔離
- ✅ **多使用者支援**：支援多個使用者同時使用，互不干擾
- ✅ **進度追蹤**：即時顯示資料收集進度
- ✅ **JSON匯出**：支援將收集的資料匯出為JSON格式

## 架構設計

### 資料庫模型

#### 1. ChatSession（聊天會話）
- 管理每個使用者的聊天會話
- 追蹤會話狀態（active, completed, abandoned）
- 與使用者一對多關係

#### 2. ChatMessage（聊天訊息）
- 儲存所有對話歷史
- 區分使用者訊息（user）和機器人回覆（assistant）
- 與聊天會話關聯

#### 3. CompanyOnboarding（公司導入資料）
- 主欄資料：
  - 公司ID（Company_ID）
  - 公司名稱（Company_Name）
  - 產業別（Industry）
  - 國家（Country）
  - 關稅（Tax）- 後端自動計算
  - 地址（Address）
  - 資本總額（Capital_Amount）
  - 發明專利數量（Invention_Patent_Count）
  - 新型專利數量（Utility_Patent_Count）
  - 公司認證資料數量（Certification_Count）
  - ESG相關認證（ESG_Certification）

#### 4. Product（產品資訊）
- 子欄資料：
  - 產品ID（Product_ID）
  - 產品名稱（Product_Name）
  - 價格（Price）
  - 主要原料（Main_Raw_Materials）
  - 產品規格（Product_Standard）
  - 技術優勢（Technical_Advantages）

## API 端點

### 1. 發送訊息給聊天機器人

**POST** `/api/chatbot/message`

**請求體：**
```json
{
  "message": "我想要開始設定我的公司資料",
  "session_id": null  // 首次對話為 null，後續使用返回的 session_id
}
```

**回應：**
```json
{
  "session_id": 1,
  "message": "您好！我是企業導入助理...",
  "completed": false,
  "progress": {
    "company_info_complete": false,
    "fields_completed": 0,
    "total_fields": 10,
    "products_count": 0
  }
}
```

### 2. 獲取使用者的所有聊天會話

**GET** `/api/chatbot/sessions`

**回應：**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "status": "active",
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:30:00",
    "completed_at": null
  }
]
```

### 3. 獲取會話的所有訊息

**GET** `/api/chatbot/sessions/{session_id}/messages`

**回應：**
```json
[
  {
    "id": 1,
    "session_id": 1,
    "role": "assistant",
    "content": "您好！我是企業導入助理...",
    "created_at": "2024-01-01T10:00:00"
  },
  {
    "id": 2,
    "session_id": 1,
    "role": "user",
    "content": "C001",
    "created_at": "2024-01-01T10:01:00"
  }
]
```

### 4. 獲取收集的資料

**GET** `/api/chatbot/data/{session_id}`

**回應：**
```json
{
  "id": 1,
  "chat_session_id": 1,
  "user_id": 1,
  "company_id": "C001",
  "company_name": "鳳梨有限公司",
  "industry": "食品業",
  "country": "台灣",
  "tax": 10,
  "address": "嘉義市東區保健街18巷20號1樓",
  "capital_amount": 20,
  "invention_patent_count": 30,
  "utility_patent_count": 30,
  "certification_count": 10,
  "esg_certification": true,
  "products": [...]
}
```

### 5. 匯出資料（中文欄位格式）

**GET** `/api/chatbot/export/{session_id}`

**回應：**
```json
{
  "公司ID": "C001",
  "公司名稱": "鳳梨有限公司",
  "產業別": "食品業",
  "國家": "台灣",
  "關稅": 0.1,
  "地址": "嘉義市東區保健街18巷20號1樓",
  "資本總額(億)": 20,
  "發明專利數量": 30,
  "新型專利數量": 30,
  "公司認證資料數量": 10,
  "ESG相關認證資料": "有",
  "產品": [
    {
      "產品ID": "P001C001",
      "產品名稱": "罐頭鳳梨 - 400克",
      "價格": "40",
      "主要原料": "鳳梨塊, 糖漿，鹽",
      "產品規格(尺寸、精度)": "400g",
      "技術優勢": "-"
    }
  ]
}
```

### 6. 匯出所有已完成的資料

**GET** `/api/chatbot/export/all`

**回應：**
```json
[
  {
    "公司ID": "C001",
    "公司名稱": "鳳梨有限公司",
    ...
  },
  {
    "公司ID": "C002",
    "公司名稱": "陳宏鋼鐵有限公司",
    ...
  }
]
```

## 聊天機器人對話流程

### 1. 開始對話
機器人會發送歡迎訊息並開始收集資料。

### 2. 資料收集順序
1. 公司ID（統一編號）
2. 公司名稱
3. 產業別
4. 國家（自動計算關稅）
5. 地址
6. 資本總額（億元）
7. 發明專利數量
8. 新型專利數量
9. 公司認證資料數量
10. ESG相關認證

### 3. 產品資訊收集
完成公司基本資料後，機器人會詢問是否新增產品。

**產品資料格式：**
```
產品ID：P001C001
產品名稱：罐頭鳳梨 - 400克
價格：40
主要原料：鳳梨塊, 糖漿，鹽
產品規格(尺寸、精度)：400g
技術優勢：-
```

### 4. 完成對話
使用者回答「完成」或「不用」時，會話標記為完成。

## 國家與關稅對應表

| 國家 | 關稅率 |
|------|--------|
| 台灣 | 10% |
| 中國 | 13% |
| 美國 | 7% |
| 日本 | 10% |
| 韓國 | 10% |
| 新加坡 | 7% |
| 越南 | 10% |
| 泰國 | 7% |
| 馬來西亞 | 6% |
| 印尼 | 11% |
| 菲律賓 | 12% |
| 印度 | 18% |

## 前端整合

### 使用方式

前端已在 `/frontend/pages/dashboard/company.vue` 整合聊天機器人UI：

1. **自動啟動**：頁面載入時自動開始對話
2. **即時對話**：使用者輸入訊息後即時獲得回應
3. **進度顯示**：視覺化顯示資料收集進度
4. **一鍵匯出**：點擊「匯出 JSON」按鈕下載資料
5. **多會話支援**：可以開始新對話

### UI 特點

- 💬 **對話介面**：類似現代即時通訊應用
- 📊 **進度條**：顯示資料收集完成度
- 🎨 **漂亮設計**：漸層背景、動畫效果
- 📱 **響應式**：支援桌面和行動裝置

## 安裝與運行

### 後端設定

1. **安裝依賴：**
```bash
cd backend
pip install -r requirements.txt
```

2. **設定環境變數：**
創建 `.env` 文件：
```env
DATABASE_URL=postgresql://user:password@host:port/database
SECRET_KEY=your-secret-key-here
API_HOST=0.0.0.0
API_PORT=8000
```

3. **啟動後端：**
```bash
python main.py
```

### 前端設定

1. **安裝依賴：**
```bash
cd frontend
npm install
```

2. **啟動開發伺服器：**
```bash
npm run dev
```

3. **訪問頁面：**
打開瀏覽器訪問：`http://localhost:3000/dashboard/company`

## 測試範例

### 使用 cURL 測試

```bash
# 1. 登入獲取 token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password"}' \
  | jq -r '.access_token')

# 2. 開始新對話
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"開始","session_id":null}'

# 3. 發送公司ID
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"C001","session_id":1}'

# 4. 匯出資料
curl -X GET http://localhost:8000/api/chatbot/export/1 \
  -H "Authorization: Bearer $TOKEN"
```

## 安全性與隔離

- ✅ **使用者認證**：所有端點需要JWT token
- ✅ **資料隔離**：每個使用者只能訪問自己的會話和資料
- ✅ **會話管理**：自動關聯使用者ID，防止資料混淆
- ✅ **授權檢查**：API層面驗證使用者權限

## 擴展性

系統設計考慮了擴展性：

1. **新增欄位**：在 `CompanyOnboarding` 模型和 `ChatbotHandler` 中添加
2. **自定義流程**：修改 `get_next_field_to_collect()` 方法
3. **智能對話**：可以整合 OpenAI GPT 或其他 LLM
4. **多語言支援**：添加語言檢測和多語言提示

## 技術棧

### 後端
- FastAPI - Web 框架
- SQLAlchemy - ORM
- PostgreSQL - 資料庫
- Pydantic - 資料驗證

### 前端
- Nuxt 3 - Vue.js 框架
- TypeScript - 類型安全
- Composables - 可重用邏輯

## 故障排除

### 常見問題

1. **資料庫連接失敗**
   - 檢查 `.env` 文件中的 `DATABASE_URL`
   - 確認資料庫服務正在運行

2. **認證失敗**
   - 確認 JWT token 有效
   - 檢查 `SECRET_KEY` 設定

3. **前端 API 調用失敗**
   - 確認後端服務正在運行
   - 檢查 CORS 設定

## 未來改進

- 🔄 支援資料編輯和修改
- 🤖 整合真實的 AI 語言模型
- 📸 支援圖片和文件上傳
- 🌐 多語言介面
- 📊 資料分析和視覺化
- 🔔 通知和提醒功能

## 聯絡與支援

如有問題或建議，請聯絡開發團隊。

---

**版本**: 1.0.0
**最後更新**: 2024-01-06
