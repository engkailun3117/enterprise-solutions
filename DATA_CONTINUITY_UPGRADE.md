# Data Continuity Upgrade Guide

## 🎯 What Was Fixed

You noticed that your database had **multiple company_onboarding records** for the same user (sessions 1, 2, 3, 4). This upgrade fixes that by:

1. ✅ **Single "Current" Record** - Only one active company record per user
2. ✅ **Update Functionality** - Users can modify existing data instead of creating duplicates
3. ✅ **Product ID Validation** - Prevents duplicate products with the same ID
4. ✅ **Historical Tracking** - Old records preserved for audit, but marked as not current

---

## 📊 Before vs After

### Before (Problem)
```
company_onboarding table:
┌────┬───────────────────┬─────────┬──────────────────┐
│ id │ chat_session_id   │ user_id │ industry         │
├────┼───────────────────┼─────────┼──────────────────┤
│ 1  │ 1                 │ 1       │ NULL             │
│ 2  │ 2                 │ 1       │ NULL             │
│ 3  │ 3                 │ 1       │ 電子業            │
│ 4  │ 4                 │ 1       │ 電子業            │  ← Duplicate!
└────┴───────────────────┴─────────┴──────────────────┘
```

**Issues:**
- Multiple records for same user
- No clear "current" state
- Duplicated product data
- Exports show all duplicates

### After (Solution)
```
company_onboarding table:
┌────┬───────────────────┬─────────┬──────────┬────────────┐
│ id │ chat_session_id   │ user_id │ industry │ is_current │
├────┼───────────────────┼─────────┼──────────┼────────────┤
│ 1  │ 1                 │ 1       │ NULL     │ FALSE      │ History
│ 2  │ 2                 │ 1       │ NULL     │ FALSE      │ History
│ 3  │ 3                 │ 1       │ 電子業    │ FALSE      │ History
│ 4  │ 4                 │ 1       │ 電子業    │ TRUE  ✓    │ Current!
└────┴───────────────────┴─────────┴──────────┴────────────┘
```

**Benefits:**
- Clear current state (is_current=True)
- Historical records preserved
- Exports show only current data
- Updates modify current record

---

## 🔧 Migration Steps

### Step 1: Run the Migration Script

```bash
cd backend
python migrate_add_is_current.py
```

**What it does:**
1. Adds `is_current` column to `company_onboarding` table
2. Creates index for better performance
3. Sets the most recent record per user as `is_current=True`
4. Shows summary of changes

**Expected Output:**
```
Adding is_current column...
Creating index on is_current...
Setting most recent record per user as current...

Migration Results:
User ID | Total Records | Current Records
---------------------------------------------
      1 |             4 |               1

✅ Migration completed successfully!
```

### Step 2: Restart Backend

```bash
# Stop current backend (Ctrl+C if running)
python main.py
```

### Step 3: Test the Changes

1. **Open test-chatbot.html**
2. **Create new session** - You should see:
   ```
   您好！歡迎回來！我看到您之前已經填寫過資料了。

   📊 目前資料概況：
   - 產業別：電子業
   - 資本額：5000000
   - 發明專利：10件
   - 產品數量：2項

   請問您想要：
   1️⃣ 更新資料 - 修改或補充現有資料
   2️⃣ 新增產品 - 新增更多產品資訊
   ...
   ```

---

## 🆕 New Features

### 1. Smart Welcome Message

**For Returning Users (Has Data):**
```
您好！歡迎回來！我看到您之前已經填寫過資料了。

📊 目前資料概況：
- 產業別：電子業
- 資本額：5000000
...

請問您想要：
1️⃣ 更新資料
2️⃣ 新增產品
3️⃣ 上傳文件
4️⃣ 查看完整資料
5️⃣ 重新開始
```

**For New Users:**
```
您好！我是企業資料收集助理。

請問您想要進行以下哪項操作？
1️⃣ 填寫資料
2️⃣ 上傳文件
...
```

### 2. Update Existing Data

Users can now say:
- "我要修改資本額"
- "更新產品資訊"
- "更正專利數量"

The AI will update the current record instead of creating a new one.

### 3. Product ID Validation

**AI Guidance:**
- "請提供產品ID（例如：PROD001、SKU-001等）"
- "產品ID必須是唯一的識別碼"

**Automatic Duplicate Handling:**
- If product ID already exists → **updates** existing product
- If product ID is new → **creates** new product

### 4. New API Endpoint

```bash
# Get current company data
GET /api/chatbot/data/current
Authorization: Bearer <jwt-token>

Response:
{
  "has_data": true,
  "data": {
    "id": 4,
    "user_id": 1,
    "industry": "電子業",
    "capital_amount": 5000000,
    "is_current": true,
    "products": [...]
  }
}
```

### 5. Export Current Data Only

```bash
# Export current data (default)
GET /api/chatbot/export/all
→ Returns only is_current=True records

# Export with history
GET /api/chatbot/export/all?include_history=true
→ Returns all completed sessions
```

---

## 💡 Usage Examples

### Example 1: Check if User Has Data

```javascript
const response = await chatbot.getCurrentData();

if (response.has_data) {
  console.log('User has existing data:', response.data);
  // Show "Continue" or "Update" options
} else {
  console.log('New user');
  // Show "Get Started" flow
}
```

### Example 2: Update Industry

**User:** "我要修改產業別"

**AI:** "好的，請問要修改成什麼產業？"

**User:** "製造業"

**AI:** "已更新產業別為「製造業」✓"

### Example 3: Add Product with Validation

**AI:** "請提供產品ID（例如：PROD001、SKU-001等）"

**User:** "PROD001"

**AI:**
- If new: "好的，產品ID：PROD001。接下來請告訴我產品名稱"
- If exists: "產品ID「PROD001」已存在，將更新該產品資訊"

---

## 🔍 Database Schema Changes

```sql
-- New column added
ALTER TABLE company_onboarding
ADD COLUMN is_current BOOLEAN DEFAULT FALSE NOT NULL;

-- New index for performance
CREATE INDEX idx_company_onboarding_is_current
ON company_onboarding(is_current);

-- Query for current data
SELECT * FROM company_onboarding
WHERE user_id = 1 AND is_current = TRUE;
```

---

## 📚 Updated API Documentation

Add to your `API_INTEGRATION_GUIDE.md`:

### Get Current Company Data

**Endpoint:** `GET /api/chatbot/data/current`

**Description:** Get the user's current (active) company onboarding data

**Response:**
```json
{
  "has_data": true,
  "data": {
    "id": 4,
    "user_id": 1,
    "industry": "電子業",
    "capital_amount": 5000000,
    "is_current": true,
    "products": [...]
  }
}
```

**Use Case:** Check if user has existing data before starting chatbot

---

## ✅ Testing Checklist

- [ ] Run migration script successfully
- [ ] Restart backend server
- [ ] Create new session - see welcome message with existing data
- [ ] Say "更新資本額" - verify it updates (not creates new)
- [ ] Add product with duplicate ID - verify it updates existing
- [ ] Check database - only one record has `is_current=TRUE`
- [ ] Call `/api/chatbot/data/current` - verify returns current data
- [ ] Export data - verify shows only current record

---

## 🎓 Key Concepts

### is_current Field

- `TRUE` = Active/Current record (only ONE per user)
- `FALSE` = Historical/Archived record

### Data Flow

```
1. User creates first session
   → Record 1: is_current=TRUE

2. User creates second session
   → Record 1: is_current=FALSE (archived)
   → Record 2: is_current=TRUE (current)
   → Data copied from Record 1 to Record 2

3. User updates data in session 2
   → Record 2: updated (still is_current=TRUE)
   → No new record created!

4. User exports data
   → Returns Record 2 only
   → Historical Record 1 preserved in DB
```

---

## 🚀 Benefits for Production

1. **Cleaner Data** - One source of truth per user
2. **Better Performance** - Indexed is_current for fast queries
3. **Audit Trail** - Historical records preserved
4. **User Experience** - Seamless updates, no confusion
5. **Integration Ready** - Main system can query current data easily

---

## 📞 Need Help?

If you encounter issues:

1. Check migration output for errors
2. Verify `is_current` column exists: `\d company_onboarding` (in psql)
3. Check current data: `SELECT * FROM company_onboarding WHERE is_current=TRUE;`
4. Review backend logs for any errors

---

**Last Updated:** 2024-01-16
**Version:** 3.1.0 (Data Continuity Update)
