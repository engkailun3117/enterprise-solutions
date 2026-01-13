# 企業導入 AI 助理 Chatbot API 文檔

## 概述

這是一個專注於**資料收集**的聊天機器人API系統，用於協助使用者通過對話方式輸入公司和產品資訊。

### 責任範圍

**本 API 僅負責：**
- ✅ 對話式資料收集（產業別、資本總額、專利數量、認證、ESG、產品資訊）
- ✅ 會話管理和對話歷史記錄
- ✅ 資料匯出為 JSON 格式

**不包含以下功能：**
- ❌ 使用者註冊/登入功能（假設使用者已存在）
- ❌ 管理員功能（Admin）
- ❌ 公司申請審核流程
- ❌ 公司 ID、公司名稱等基本資訊收集（由其他系統負責）

### 系統特點

-  **對話式資料收集**：透過自然對話引導使用者輸入資料
-  **會話記憶**：每個使用者擁有獨立的聊天會話，確保資料隔離
-  **多使用者支援**：支援多個使用者同時使用，互不干擾
-  **進度追蹤**：即時顯示資料收集進度
-  **JSON匯出**：支援將收集的資料匯出為JSON格式

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

#### 3. CompanyOnboarding（聊天機器人收集資料）
- 聊天機器人責任範圍：
  - 產業別（Industry）
  - 資本總額（Capital_Amount）- 以臺幣為單位
  - 發明專利數量（Invention_Patent_Count）
  - 新型專利數量（Utility_Patent_Count）
  - 公司認證資料數量（Certification_Count）
  - ESG相關認證（ESG_Certification）

#### 4. Product（產品資訊）
- 產品資料：
  - 產品ID（Product_ID）
  - 產品名稱（Product_Name）
  - 價格（Price）
  - 主要原料（Main_Raw_Materials）
  - 產品規格（Product_Standard）
  - 技術優勢（Technical_Advantages）

## API 端點總覽

| 方法 | 端點 | 描述 | 認證 |
|------|------|------|------|
| POST | `/api/auth/login` | 使用者登入，獲取 JWT token | ❌ |
| POST | `/api/chatbot/message` | 發送訊息給聊天機器人 | ✅ |
| GET | `/api/chatbot/sessions` | 獲取所有聊天會話 | ✅ |
| GET | `/api/chatbot/sessions/latest` | 獲取最新活躍會話 | ✅ |
| POST | `/api/chatbot/sessions/new` | 創建新會話並複製資料 | ✅ |
| GET | `/api/chatbot/sessions/{session_id}/messages` | 獲取會話的所有訊息 | ✅ |
| GET | `/api/chatbot/data/{session_id}` | 獲取收集的資料（英文欄位） | ✅ |
| GET | `/api/chatbot/export/{session_id}` | 匯出資料（中文欄位） | ✅ |
| GET | `/api/chatbot/export/all` | 匯出所有已完成的資料 | ✅ |

## 認證與授權

### JWT Token 認證

所有聊天機器人 API 端點都需要 JWT Bearer Token 認證。

**⚠️ 注意：** 本文檔假設使用者帳號已由其他系統創建。聊天機器人 API 不負責使用者註冊功能。

**獲取 Token（使用已存在的帳號）：**

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

**回應：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**使用 Token：**

所有後續請求都需要在 Header 中包含：
```
Authorization: Bearer <your_token>
Content-Type: application/json
```

**Token 有效期：** 24 小時

**安全特性：**
-  所有端點都需要有效的 JWT token
-  使用者只能訪問自己的會話和資料
-  自動驗證使用者是否啟用（is_active = true）
-  Token 使用 HS256 演算法加密

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
  "industry": "食品業",
  "capital_amount": 20,
  "invention_patent_count": 30,
  "utility_patent_count": 30,
  "certification_count": 10,
  "esg_certification": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:30:00",
  "products": [...]
}
```

### 5. 匯出資料（中文欄位格式）

**GET** `/api/chatbot/export/{session_id}`

**回應：**
```json
{
  "產業別": "食品業",
  "資本總額（以臺幣為單位）": 200000000,
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

### 7. 獲取最新活躍會話

**GET** `/api/chatbot/sessions/latest`

**用途：** 避免在頁面重新整理時創建重複會話

**回應：**
```json
{
  "session_id": 1,
  "status": "active"
}
```

如果沒有活躍會話，回應為：
```json
{
  "session_id": null,
  "status": null
}
```

### 8. 創建新會話

**POST** `/api/chatbot/sessions/new`

**用途：** 創建新會話並智能複製最新的公司資料

**特點：**
- 自動複製使用者最新的公司資料到新會話
- 避免重複輸入相同資訊
- 允許使用者更新或修改資料

**回應：**
```json
{
  "session_id": 2,
  "message": "已為您建立新的對話，並複製了您先前輸入的公司資料。您可以直接新增產品資料，或者更新公司資訊。",
  "company_info_copied": true,
  "progress": {
    "company_info_complete": true,
    "fields_completed": 10,
    "total_fields": 10,
    "products_count": 0
  }
}
```

## 聊天機器人對話流程

### 1. 開始對話
機器人會發送歡迎訊息並開始收集資料。

### 2. 資料收集順序（聊天機器人責任範圍）
1. 產業別
2. 資本總額（臺幣）
3. 發明專利數量
4. 新型專利數量
5. 公司認證資料數量
6. ESG相關認證

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

## 聊天機器人模式

系統支援兩種聊天機器人模式，可透過環境變數配置：

### 1. AI 驅動模式（預設）

**啟用方式：**
```env
USE_AI_CHATBOT=true
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini  # 可選，預設值
```

**特點：**
-  使用 OpenAI GPT 模型進行智能對話
-  自然語言理解，支援更靈活的輸入
-  可以一次提取多個欄位的資料
-  使用函數調用（Function Calling）進行結構化資料提取
-  更友善的對話體驗
-  支援中文對話

**支援的 AI 函數：**
1. `update_company_data` - 提取公司資訊
2. `add_product` - 新增產品資料
3. `mark_completed` - 標記對話完成

**範例對話：**
```
使用者：我們公司是食品業，資本額2億，有30個發明專利和15個新型專利
機器人：好的！我已經記錄了以下資訊：
         - 產業別：食品業
         - 資本總額：200000000 臺幣
         - 發明專利數量：30
         - 新型專利數量：15

         請問您的公司有多少份認證資料？
```

### 2. 規則式模式

**啟用方式：**
```env
USE_AI_CHATBOT=false
# 或不設定 OPENAI_API_KEY
```

**特點：**
-  基於預定義規則和流程
-  按固定順序收集資料
-  使用正則表達式提取資料
-  不需要 OpenAI API 金鑰
-  更快的回應速度
-  更低的運行成本

**資料收集順序：**
1. 產業別
2. 資本總額
3. 發明專利數量
4. 新型專利數量
5. 公司認證數量
6. ESG 認證
7. 產品資訊

### 模式選擇建議

| 特性 | AI 驅動模式 | 規則式模式 |
|------|------------|-----------|
| 對話靈活性 | 高 | 中 |
| 使用者體驗 | 優秀 | 良好 |
| 回應速度 | 中等（1-3秒） | 快（<100ms） |
| 運行成本 | 需要 API 費用 | 免費 |
| 多欄位同時輸入 | 支援 | 不支援 |
| 設定複雜度 | 需要 API 金鑰 | 簡單 |

## 前端整合

### 使用方式

前端已在 `/frontend/pages/dashboard/company.vue` 整合聊天機器人UI：

1. **自動啟動**：頁面載入時自動開始對話
2. **即時對話**：使用者輸入訊息後即時獲得回應
3. **進度顯示**：視覺化顯示資料收集進度
4. **一鍵匯出**：點擊「匯出 JSON」按鈕下載資料
5. **多會話支援**：可以開始新對話

### UI 特點

-  **對話介面**：類似現代即時通訊應用
-  **進度條**：顯示資料收集完成度
-  **漂亮設計**：漸層背景、動畫效果
-  **響應式**：支援桌面和行動裝置

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

# AI 聊天機器人設定（可選）
USE_AI_CHATBOT=true  # 設為 false 使用規則式模式
OPENAI_API_KEY=your_openai_api_key_here  # AI 模式需要
OPENAI_MODEL=gpt-4o-mini  # 可選，預設為 gpt-4o-mini
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

# 2. 檢查是否有活躍會話
curl -X GET http://localhost:8000/api/chatbot/sessions/latest \
  -H "Authorization: Bearer $TOKEN"

# 3. 開始新對話
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"開始","session_id":null}'

# 4. 發送公司資訊（AI 模式可一次發送多個資料）
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"我們公司產業是食品業，資本額200000000元","session_id":1}'

# 5. 查看會話訊息歷史
curl -X GET http://localhost:8000/api/chatbot/sessions/1/messages \
  -H "Authorization: Bearer $TOKEN"

# 6. 獲取收集的資料
curl -X GET http://localhost:8000/api/chatbot/data/1 \
  -H "Authorization: Bearer $TOKEN"

# 7. 匯出資料（中文格式）
curl -X GET http://localhost:8000/api/chatbot/export/1 \
  -H "Authorization: Bearer $TOKEN"

# 8. 創建新會話（會複製現有資料）
curl -X POST http://localhost:8000/api/chatbot/sessions/new \
  -H "Authorization: Bearer $TOKEN"
```

### 使用 Python 測試

```python
import requests

# 基礎 URL
BASE_URL = "http://localhost:8000"

# 1. 登入
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "testuser", "password": "password"}
)
token = response.json()["access_token"]

# 設定 headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 2. 開始對話
response = requests.post(
    f"{BASE_URL}/api/chatbot/message",
    headers=headers,
    json={"message": "開始", "session_id": None}
)
data = response.json()
session_id = data["session_id"]
print(f"會話 ID: {session_id}")
print(f"機器人回應: {data['message']}")

# 3. 發送資料
response = requests.post(
    f"{BASE_URL}/api/chatbot/message",
    headers=headers,
    json={
        "message": "我們公司是食品業，資本額200000000元，有30個發明專利和15個新型專利",
        "session_id": session_id
    }
)
print(f"進度: {response.json()['progress']}")

# 4. 匯出資料
response = requests.get(
    f"{BASE_URL}/api/chatbot/export/{session_id}",
    headers=headers
)
print(f"匯出資料: {response.json()}")
```

### 使用 JavaScript/TypeScript 測試

```typescript
const BASE_URL = 'http://localhost:8000';

// 1. 登入
async function login(username: string, password: string) {
  const response = await fetch(`${BASE_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  const data = await response.json();
  return data.access_token;
}

// 2. 發送訊息
async function sendMessage(token: string, message: string, sessionId: number | null) {
  const response = await fetch(`${BASE_URL}/api/chatbot/message`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message, session_id: sessionId })
  });
  return await response.json();
}

// 3. 完整範例
async function example() {
  // 登入
  const token = await login('testuser', 'password');

  // 開始對話
  let response = await sendMessage(token, '開始', null);
  const sessionId = response.session_id;
  console.log('會話 ID:', sessionId);

  // 發送公司資料
  response = await sendMessage(
    token,
    '我們公司是食品業，資本額200000000元，有30個發明專利',
    sessionId
  );
  console.log('進度:', response.progress);

  // 匯出資料
  const exportResponse = await fetch(
    `${BASE_URL}/api/chatbot/export/${sessionId}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const exportData = await exportResponse.json();
  console.log('匯出資料:', exportData);
}

example();
```

## 安全性與隔離

-  **使用者認證**：所有端點需要JWT token
-  **資料隔離**：每個使用者只能訪問自己的會話和資料
-  **會話管理**：自動關聯使用者ID，防止資料混淆
-  **授權檢查**：API層面驗證使用者權限

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

## HTTP 狀態碼與錯誤處理

### 成功回應
- **200 OK**: 請求成功
- **201 Created**: 資源創建成功

### 客戶端錯誤
- **400 Bad Request**: 請求格式錯誤或缺少必要參數
  ```json
  {
    "detail": "Validation error: message field is required"
  }
  ```

- **401 Unauthorized**: Token 無效或已過期
  ```json
  {
    "detail": "Could not validate credentials"
  }
  ```

- **403 Forbidden**: 使用者帳號未啟用
  ```json
  {
    "detail": "User account is not active"
  }
  ```

- **404 Not Found**: 資源不存在
  ```json
  {
    "detail": "Chat session not found"
  }
  ```

### 伺服器錯誤
- **500 Internal Server Error**: 伺服器內部錯誤
  ```json
  {
    "detail": "Internal server error"
  }
  ```

### 錯誤處理最佳實踐

```python
import requests

def safe_api_call(url, headers, json_data=None, method='GET'):
    """安全的 API 調用範例"""
    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, json=json_data)
        else:
            response = requests.get(url, headers=headers)

        # 檢查狀態碼
        if response.status_code == 401:
            print("Token 已過期，請重新登入")
            return None
        elif response.status_code == 404:
            print("資源不存在")
            return None
        elif response.status_code >= 400:
            print(f"錯誤: {response.json().get('detail', '未知錯誤')}")
            return None

        return response.json()

    except requests.exceptions.ConnectionError:
        print("無法連接到伺服器")
        return None
    except requests.exceptions.Timeout:
        print("請求超時")
        return None
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        return None
```

```typescript
// TypeScript 錯誤處理範例
async function safeApiCall<T>(
  url: string,
  options: RequestInit
): Promise<T | null> {
  try {
    const response = await fetch(url, options);

    if (response.status === 401) {
      console.error('Token 已過期，請重新登入');
      // 觸發重新登入流程
      return null;
    }

    if (response.status === 404) {
      console.error('資源不存在');
      return null;
    }

    if (!response.ok) {
      const error = await response.json();
      console.error('API 錯誤:', error.detail);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('網路錯誤:', error);
    return null;
  }
}
```

## 故障排除

### 常見問題

1. **資料庫連接失敗**
   - 檢查 `.env` 文件中的 `DATABASE_URL`
   - 確認資料庫服務正在運行
   - 檢查資料庫連接字串格式：`postgresql://user:password@host:port/database`

2. **認證失敗 (401 錯誤)**
   - 確認 JWT token 有效且未過期
   - 檢查 `SECRET_KEY` 設定
   - 確認 Authorization header 格式：`Bearer <token>`
   - Token 有效期為 24 小時，過期需重新登入

3. **使用者帳號無法使用 (403 錯誤)**
   - 確認使用者的 `is_active` 欄位為 `true`
   - 聯絡管理員啟用帳號

4. **前端 API 調用失敗**
   - 確認後端服務正在運行（預設端口 8000）
   - 檢查 CORS 設定
   - 使用瀏覽器開發者工具檢查網路請求
   - 確認 API URL 正確

5. **會話不存在 (404 錯誤)**
   - 確認 session_id 正確
   - 確認該會話屬於當前使用者
   - 使用 `/api/chatbot/sessions/latest` 獲取最新會話

6. **OpenAI API 錯誤**
   - 確認 `OPENAI_API_KEY` 設定正確
   - 檢查 API 配額是否用完
   - 如果 OpenAI 服務不可用，設定 `USE_AI_CHATBOT=false` 使用規則式模式

7. **資料提取不正確**
   - AI 模式：檢查提示詞和函數定義
   - 規則式模式：檢查正則表達式是否匹配輸入格式
   - 確認輸入資料格式符合預期

8. **進度追蹤不準確**
   - 刷新會話資料：重新調用 `/api/chatbot/message` 或 `/api/chatbot/data/{session_id}`
   - 檢查資料庫中的 `company_onboarding` 表格

## 使用情境範例

### 情境 1：首次使用聊天機器人

```bash
# 1. 登入
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123"}' \
  | jq -r '.access_token')

# 2. 檢查是否有活躍會話
curl -X GET http://localhost:8000/api/chatbot/sessions/latest \
  -H "Authorization: Bearer $TOKEN"
# 回應: {"session_id": null, "status": null}

# 3. 開始對話
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"開始","session_id":null}'

# 4. 繼續對話...
```

### 情境 2：繼續之前的會話

```bash
# 1. 獲取最新會話
LATEST=$(curl -X GET http://localhost:8000/api/chatbot/sessions/latest \
  -H "Authorization: Bearer $TOKEN")
SESSION_ID=$(echo $LATEST | jq -r '.session_id')

# 2. 查看歷史訊息
curl -X GET http://localhost:8000/api/chatbot/sessions/$SESSION_ID/messages \
  -H "Authorization: Bearer $TOKEN"

# 3. 繼續對話
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"繼續\",\"session_id\":$SESSION_ID}"
```

### 情境 3：新增另一份資料

```bash
# 1. 創建新會話（會複製上一次的資料）
NEW_SESSION=$(curl -X POST http://localhost:8000/api/chatbot/sessions/new \
  -H "Authorization: Bearer $TOKEN")
NEW_SESSION_ID=$(echo $NEW_SESSION | jq -r '.session_id')

# 2. 開始修改或新增資料
curl -X POST http://localhost:8000/api/chatbot/message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"我要修改資本額為500000000元\",\"session_id\":$NEW_SESSION_ID}"
```

### 情境 4：完整流程（使用 AI 模式）

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 登入
response = requests.post(f"{BASE_URL}/api/auth/login",
    json={"username": "user1", "password": "pass123"})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. 開始對話
response = requests.post(f"{BASE_URL}/api/chatbot/message",
    headers=headers,
    json={"message": "開始", "session_id": None})
session_id = response.json()["session_id"]

# 3. AI 模式：一次提供多個資料
response = requests.post(f"{BASE_URL}/api/chatbot/message",
    headers=headers,
    json={
        "message": """
        產業別：資訊科技業
        資本總額：500000000元
        發明專利：100個
        新型專利：50個
        公司認證：20個
        有 ESG 認證
        """,
        "session_id": session_id
    })

# 4. 新增產品
response = requests.post(f"{BASE_URL}/api/chatbot/message",
    headers=headers,
    json={
        "message": """
        產品ID：P001
        產品名稱：AI 智能分析系統
        價格：100000
        主要原料：軟體授權
        產品規格：雲端部署，支援 1000 並發用戶
        技術優勢：使用最新的深度學習技術
        """,
        "session_id": session_id
    })

# 5. 完成對話
response = requests.post(f"{BASE_URL}/api/chatbot/message",
    headers=headers,
    json={"message": "完成", "session_id": session_id})

# 6. 匯出資料
response = requests.get(f"{BASE_URL}/api/chatbot/export/{session_id}",
    headers=headers)
print("匯出資料:", response.json())
```

## 最佳實踐

### 1. Token 管理
- 在本地儲存 token（但要安全地儲存）
- 檢查 token 過期時間
- 401 錯誤時自動重新登入

### 2. 會話管理
- 頁面載入時檢查是否有活躍會話
- 避免創建重複會話
- 使用 `/sessions/latest` 而不是猜測 session_id

### 3. 錯誤處理
- 所有 API 調用都應有錯誤處理
- 提供使用者友善的錯誤訊息
- 記錄錯誤以便除錯

### 4. 資料驗證
- 前端進行基本驗證
- 後端會進行完整驗證
- 顯示清楚的驗證錯誤訊息

### 5. 性能優化
- 避免頻繁調用 API
- 使用 debounce 處理使用者輸入
- 快取不常變動的資料

## 未來改進

-  **已完成**：AI 驅動的智能對話
-  支援資料編輯和修改
-  支援圖片和文件上傳

## 聯絡與支援

如有問題或建議，請聯絡開發團隊。

---

**版本**: 3.0.0
**最後更新**: 2026-01-12
**更新內容**:
- **重大變更**: 調整聊天機器人責任範圍，僅收集以下資料：
  - 產業別、資本總額、發明專利數量、新型專利數量、公司認證數量、ESG認證、產品資訊
  - 移除：公司ID、公司名稱、國家、關稅、地址（不再由聊天機器人收集）
- 移除 `/api/chatbot/submit-application` 端點
- 更新所有 API 回應格式以反映新的資料結構
- 更新文件範例和測試程式碼
