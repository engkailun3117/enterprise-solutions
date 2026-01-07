"""
AI-Powered Chatbot Handler for Company Onboarding Assistant
Uses OpenAI GPT for intelligent conversation and data extraction
"""

import json
import os
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from openai import OpenAI
from models import ChatSession, ChatMessage, CompanyOnboarding, Product, ChatSessionStatus
from config import get_settings

# Initialize settings
settings = get_settings()

# OpenAI client will be initialized lazily
_client = None

def get_openai_client():
    """Lazy initialize OpenAI client"""
    global _client
    if _client is None and settings.openai_api_key:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


# Country to tax rate mapping (as percentage * 100, e.g., 10 = 10%)
COUNTRY_TAX_MAPPING = {
    "台灣": 10,
    "中國": 13,
    "美國": 7,
    "日本": 10,
    "韓國": 10,
    "新加坡": 7,
    "越南": 10,
    "泰國": 7,
    "馬來西亞": 6,
    "印尼": 11,
    "菲律賓": 12,
    "印度": 18,
}


class AIChatbotHandler:
    """AI-powered chatbot handler using OpenAI"""

    def __init__(self, db: Session, user_id: int, session_id: Optional[int] = None):
        self.db = db
        self.user_id = user_id
        self.session_id = session_id
        self.session = None
        self.onboarding_data = None

        # Load or create session
        if session_id:
            self.session = db.query(ChatSession).filter(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            ).first()

            if self.session:
                self.onboarding_data = db.query(CompanyOnboarding).filter(
                    CompanyOnboarding.chat_session_id == session_id
                ).first()

    def create_session(self) -> ChatSession:
        """Create a new chat session"""
        self.session = ChatSession(
            user_id=self.user_id,
            status=ChatSessionStatus.ACTIVE
        )
        self.db.add(self.session)
        self.db.commit()
        self.db.refresh(self.session)

        # Create empty onboarding data
        self.onboarding_data = CompanyOnboarding(
            chat_session_id=self.session.id,
            user_id=self.user_id
        )
        self.db.add(self.onboarding_data)
        self.db.commit()
        self.db.refresh(self.onboarding_data)

        return self.session

    def get_conversation_history(self) -> List[ChatMessage]:
        """Get conversation history for current session"""
        if not self.session:
            return []

        return self.db.query(ChatMessage).filter(
            ChatMessage.session_id == self.session.id
        ).order_by(ChatMessage.created_at).all()

    def add_message(self, role: str, content: str) -> ChatMessage:
        """Add a message to the conversation"""
        message = ChatMessage(
            session_id=self.session.id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_system_prompt(self) -> str:
        """Get the system prompt for the AI"""
        return """你是一個專業的企業導入助理，負責協助使用者建立公司資料。你的任務是：

1. 用友善、專業的態度與使用者對話
2. 從對話中提取以下公司資訊：
   - 公司ID（統一編號）
   - 公司名稱
   - 產業別（如：食品業、鋼鐵業、電子業等）
   - 國家（台灣、中國、美國、日本等）
   - 地址
   - 資本總額（以億元為單位）
   - 發明專利數量
   - 新型專利數量
   - 公司認證資料數量
   - ESG相關認證（有/無）

3. 收集產品資訊（可以有多個產品）：
   - 產品ID
   - 產品名稱
   - 價格
   - 主要原料
   - 產品規格（尺寸、精度）
   - 技術優勢

重要提示：
- 如果使用者一次提供多個資訊，請一次提取所有資訊
- 如果資訊不清楚，請禮貌地詢問
- 當收集完所有資訊後，詢問使用者是否還要新增產品
- 保持對話自然流暢

可用國家列表：""" + ", ".join(COUNTRY_TAX_MAPPING.keys())

    def get_current_data_summary(self) -> str:
        """Get a summary of currently collected data"""
        if not self.onboarding_data:
            return "尚未收集任何資料"

        data = []
        if self.onboarding_data.company_id:
            data.append(f"公司ID: {self.onboarding_data.company_id}")
        if self.onboarding_data.company_name:
            data.append(f"公司名稱: {self.onboarding_data.company_name}")
        if self.onboarding_data.industry:
            data.append(f"產業別: {self.onboarding_data.industry}")
        if self.onboarding_data.country:
            data.append(f"國家: {self.onboarding_data.country}")
        if self.onboarding_data.address:
            data.append(f"地址: {self.onboarding_data.address}")
        if self.onboarding_data.capital_amount is not None:
            data.append(f"資本總額: {self.onboarding_data.capital_amount}億")
        if self.onboarding_data.invention_patent_count is not None:
            data.append(f"發明專利: {self.onboarding_data.invention_patent_count}件")
        if self.onboarding_data.utility_patent_count is not None:
            data.append(f"新型專利: {self.onboarding_data.utility_patent_count}件")
        if self.onboarding_data.certification_count is not None:
            data.append(f"認證資料: {self.onboarding_data.certification_count}份")
        if self.onboarding_data.esg_certification is not None:
            data.append(f"ESG認證: {'有' if self.onboarding_data.esg_certification else '無'}")

        products_count = len(self.onboarding_data.products) if self.onboarding_data.products else 0
        if products_count > 0:
            data.append(f"產品數量: {products_count}個")

        return "\n".join(data) if data else "尚未收集任何資料"

    def extract_data_with_ai(self, user_message: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Use OpenAI to extract structured data from conversation"""
        client = get_openai_client()
        if not client:
            return {"error": "OpenAI API key not configured"}

        # Build conversation for OpenAI
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "system", "content": f"目前已收集的資料：\n{self.get_current_data_summary()}"}
        ]

        # Add recent conversation history (last 10 messages)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Define function for structured data extraction
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "update_company_data",
                    "description": "更新公司資料。從使用者的訊息中提取資訊並更新。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "company_id": {"type": "string", "description": "公司ID或統一編號"},
                            "company_name": {"type": "string", "description": "公司名稱"},
                            "industry": {"type": "string", "description": "產業別"},
                            "country": {"type": "string", "description": "國家"},
                            "address": {"type": "string", "description": "地址"},
                            "capital_amount": {"type": "integer", "description": "資本總額（億元）"},
                            "invention_patent_count": {"type": "integer", "description": "發明專利數量"},
                            "utility_patent_count": {"type": "integer", "description": "新型專利數量"},
                            "certification_count": {"type": "integer", "description": "公司認證資料數量"},
                            "esg_certification": {"type": "boolean", "description": "是否有ESG相關認證"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_product",
                    "description": "新增產品資訊",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "string", "description": "產品ID"},
                            "product_name": {"type": "string", "description": "產品名稱"},
                            "price": {"type": "string", "description": "價格"},
                            "main_raw_materials": {"type": "string", "description": "主要原料"},
                            "product_standard": {"type": "string", "description": "產品規格"},
                            "technical_advantages": {"type": "string", "description": "技術優勢"}
                        },
                        "required": ["product_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mark_completed",
                    "description": "當使用者表示已完成所有資料輸入時調用此函數",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "completed": {"type": "boolean", "description": "是否完成"}
                        },
                        "required": ["completed"]
                    }
                }
            }
        ]

        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            result = {
                "message": response.choices[0].message.content or "",
                "function_calls": []
            }

            # Process tool calls
            if response.choices[0].message.tool_calls:
                for tool_call in response.choices[0].message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    result["function_calls"].append({
                        "name": function_name,
                        "arguments": function_args
                    })

            return result

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {
                "error": str(e),
                "message": "抱歉，我遇到了一些技術問題。請稍後再試。"
            }

    def update_onboarding_data(self, data: Dict[str, Any]) -> bool:
        """Update onboarding data with extracted information"""
        try:
            updated = False

            if "company_id" in data and data["company_id"]:
                self.onboarding_data.company_id = data["company_id"]
                updated = True

            if "company_name" in data and data["company_name"]:
                self.onboarding_data.company_name = data["company_name"]
                updated = True

            if "industry" in data and data["industry"]:
                self.onboarding_data.industry = data["industry"]
                updated = True

            if "country" in data and data["country"]:
                country = data["country"]
                self.onboarding_data.country = country
                # Auto-set tax based on country
                self.onboarding_data.tax = COUNTRY_TAX_MAPPING.get(country, 10)
                updated = True

            if "address" in data and data["address"]:
                self.onboarding_data.address = data["address"]
                updated = True

            if "capital_amount" in data and data["capital_amount"] is not None:
                self.onboarding_data.capital_amount = int(data["capital_amount"])
                updated = True

            if "invention_patent_count" in data and data["invention_patent_count"] is not None:
                self.onboarding_data.invention_patent_count = int(data["invention_patent_count"])
                updated = True

            if "utility_patent_count" in data and data["utility_patent_count"] is not None:
                self.onboarding_data.utility_patent_count = int(data["utility_patent_count"])
                updated = True

            if "certification_count" in data and data["certification_count"] is not None:
                self.onboarding_data.certification_count = int(data["certification_count"])
                updated = True

            if "esg_certification" in data and data["esg_certification"] is not None:
                self.onboarding_data.esg_certification = bool(data["esg_certification"])
                updated = True

            if updated:
                self.db.commit()

            return updated

        except Exception as e:
            print(f"Error updating onboarding data: {e}")
            self.db.rollback()
            return False

    def add_product(self, product_data: Dict[str, Any]) -> Optional[Product]:
        """Add a product to the onboarding data"""
        try:
            product = Product(
                onboarding_id=self.onboarding_data.id,
                product_id=product_data.get("product_id"),
                product_name=product_data.get("product_name"),
                price=product_data.get("price"),
                main_raw_materials=product_data.get("main_raw_materials"),
                product_standard=product_data.get("product_standard"),
                technical_advantages=product_data.get("technical_advantages")
            )
            self.db.add(product)
            self.db.commit()
            self.db.refresh(product)
            return product
        except Exception as e:
            print(f"Error adding product: {e}")
            self.db.rollback()
            return None

    def process_message(self, user_message: str) -> tuple[str, bool]:
        """
        Process user message with AI and return bot response
        Returns: (response_message, is_completed)
        """
        # Get conversation history
        history = self.get_conversation_history()
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history
        ]

        # Extract data with AI
        ai_result = self.extract_data_with_ai(user_message, conversation_history)

        if "error" in ai_result:
            return ai_result.get("message", "抱歉，發生錯誤。"), False

        # Process function calls
        completed = False
        if "function_calls" in ai_result:
            for call in ai_result["function_calls"]:
                if call["name"] == "update_company_data":
                    self.update_onboarding_data(call["arguments"])
                elif call["name"] == "add_product":
                    self.add_product(call["arguments"])
                elif call["name"] == "mark_completed":
                    if call["arguments"].get("completed"):
                        self.session.status = ChatSessionStatus.COMPLETED
                        self.db.commit()
                        completed = True

        # Return AI response
        response_message = ai_result.get("message", "")
        if not response_message:
            response_message = "我已經記錄您的資訊。請繼續提供其他資料。"

        return response_message, completed

    def get_progress(self) -> Dict[str, Any]:
        """Get current progress of data collection"""
        fields_completed = 0
        total_fields = 10

        if self.onboarding_data.company_id:
            fields_completed += 1
        if self.onboarding_data.company_name:
            fields_completed += 1
        if self.onboarding_data.industry:
            fields_completed += 1
        if self.onboarding_data.country:
            fields_completed += 1
        if self.onboarding_data.address:
            fields_completed += 1
        if self.onboarding_data.capital_amount is not None:
            fields_completed += 1
        if self.onboarding_data.invention_patent_count is not None:
            fields_completed += 1
        if self.onboarding_data.utility_patent_count is not None:
            fields_completed += 1
        if self.onboarding_data.certification_count is not None:
            fields_completed += 1
        if self.onboarding_data.esg_certification is not None:
            fields_completed += 1

        return {
            "company_info_complete": fields_completed == total_fields,
            "fields_completed": fields_completed,
            "total_fields": total_fields,
            "products_count": len(self.onboarding_data.products) if self.onboarding_data.products else 0
        }
