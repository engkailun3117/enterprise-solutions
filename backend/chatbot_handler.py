"""
Chatbot Handler for Company Onboarding Assistant
Manages conversation flow and data extraction
"""

import re
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from models import ChatSession, ChatMessage, CompanyOnboarding, Product, ChatSessionStatus


class ConversationState:
    """Tracks the current state of the conversation"""

    # Chatbot collected fields (責任範圍)
    INDUSTRY = "industry"
    CAPITAL_AMOUNT = "capital_amount"
    INVENTION_PATENT_COUNT = "invention_patent_count"
    UTILITY_PATENT_COUNT = "utility_patent_count"
    CERTIFICATION_COUNT = "certification_count"
    ESG_CERTIFICATION = "esg_certification"

    # Product information
    PRODUCTS = "products"
    ADDING_PRODUCTS = "adding_products"

    # Flow states
    COMPLETED = "completed"


class ChatbotHandler:
    """Handles chatbot conversation logic"""

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

    def get_next_field_to_collect(self) -> Optional[str]:
        """Determine the next field to collect based on current data"""
        # Only collect fields within chatbot's responsibility
        if not self.onboarding_data.industry:
            return ConversationState.INDUSTRY
        if self.onboarding_data.capital_amount is None:
            return ConversationState.CAPITAL_AMOUNT
        if self.onboarding_data.invention_patent_count is None:
            return ConversationState.INVENTION_PATENT_COUNT
        if self.onboarding_data.utility_patent_count is None:
            return ConversationState.UTILITY_PATENT_COUNT
        if self.onboarding_data.certification_count is None:
            return ConversationState.CERTIFICATION_COUNT
        if self.onboarding_data.esg_certification is None:
            return ConversationState.ESG_CERTIFICATION

        # Check if we've asked about products
        history = self.get_conversation_history()
        asked_about_products = any("產品" in msg.content and msg.role == "assistant" for msg in history[-5:])

        if not asked_about_products:
            return ConversationState.ADDING_PRODUCTS

        return ConversationState.COMPLETED

    def extract_and_save_data(self, user_message: str, field: str) -> bool:
        """Extract data from user message and save to database"""
        try:
            # Only collect fields within chatbot's responsibility
            if field == ConversationState.INDUSTRY:
                self.onboarding_data.industry = user_message.strip()

            elif field == ConversationState.CAPITAL_AMOUNT:
                # Extract number from message
                numbers = re.findall(r'\d+', user_message)
                if numbers:
                    self.onboarding_data.capital_amount = int(numbers[0])
                else:
                    return False

            elif field == ConversationState.INVENTION_PATENT_COUNT:
                numbers = re.findall(r'\d+', user_message)
                if numbers:
                    self.onboarding_data.invention_patent_count = int(numbers[0])
                else:
                    return False

            elif field == ConversationState.UTILITY_PATENT_COUNT:
                numbers = re.findall(r'\d+', user_message)
                if numbers:
                    self.onboarding_data.utility_patent_count = int(numbers[0])
                else:
                    return False

            elif field == ConversationState.CERTIFICATION_COUNT:
                numbers = re.findall(r'\d+', user_message)
                if numbers:
                    self.onboarding_data.certification_count = int(numbers[0])
                else:
                    return False

            elif field == ConversationState.ESG_CERTIFICATION:
                msg_lower = user_message.lower()
                if any(word in msg_lower for word in ["有", "yes", "是", "對", "有的"]):
                    self.onboarding_data.esg_certification = True
                elif any(word in msg_lower for word in ["無", "no", "沒有", "否", "沒"]):
                    self.onboarding_data.esg_certification = False
                else:
                    return False

            self.db.commit()
            return True

        except Exception as e:
            print(f"Error extracting data: {e}")
            return False

    def extract_product_data(self, user_message: str) -> Optional[Dict[str, Any]]:
        """Extract product information from user message"""
        # Simple extraction - can be enhanced with NLP
        product_data = {}

        # Try to extract structured data
        lines = user_message.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line or '：' in line:
                parts = re.split('[：:]', line, 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()

                    if any(k in key for k in ["產品ID", "产品ID"]):
                        product_data["product_id"] = value
                    elif any(k in key for k in ["產品名稱", "产品名称", "名稱", "名称"]):
                        product_data["product_name"] = value
                    elif any(k in key for k in ["價格", "价格"]):
                        product_data["price"] = value
                    elif any(k in key for k in ["原料", "主要原料"]):
                        product_data["main_raw_materials"] = value
                    elif any(k in key for k in ["規格", "规格", "尺寸", "精度"]):
                        product_data["product_standard"] = value
                    elif any(k in key for k in ["技術優勢", "技术优势", "優勢", "优势"]):
                        product_data["technical_advantages"] = value

        return product_data if product_data else None

    def add_product(self, product_data: Dict[str, Any]) -> Product:
        """Add a product to the onboarding data"""
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

    def get_initial_greeting(self) -> str:
        """Get the initial greeting with menu options"""
        return """您好！我是企業資料收集助理。

請問您想要進行以下哪項操作？

1️⃣ 填寫資料 - 開始收集公司和產品資料
2️⃣ 查看進度 - 了解目前資料填寫的進度如何
3️⃣ 查看已填資料 - 查看目前已經填寫的資料內容

請輸入數字（1、2 或 3）或直接說明您的需求。"""

    def get_current_data_summary(self) -> str:
        """Get a summary of currently collected data"""
        if not self.onboarding_data:
            return "尚未收集任何資料"

        data = []
        # Only collect fields within chatbot's responsibility
        if self.onboarding_data.industry:
            data.append(f"產業別: {self.onboarding_data.industry}")
        if self.onboarding_data.capital_amount is not None:
            data.append(f"資本總額: {self.onboarding_data.capital_amount} 臺幣")
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

    def get_prompt_for_field(self, field: str) -> str:
        """Get the chatbot prompt for collecting a specific field"""
        # Only collect fields within chatbot's responsibility
        prompts = {
            ConversationState.INDUSTRY: "請問您的公司所屬產業別是什麼？（例如：食品業、鋼鐵業、電子業等）",
            ConversationState.CAPITAL_AMOUNT: "請問您的公司資本總額是多少？（以臺幣為單位，請輸入數字）",
            ConversationState.INVENTION_PATENT_COUNT: "請問您的公司擁有多少件發明專利？（請輸入數字）",
            ConversationState.UTILITY_PATENT_COUNT: "請問您的公司擁有多少件新型專利？（請輸入數字）",
            ConversationState.CERTIFICATION_COUNT: "請問您的公司擁有多少份認證資料？（請輸入數字）",
            ConversationState.ESG_CERTIFICATION: "請問您的公司是否有ESG相關認證資料？（請回答：有 或 無）",
            ConversationState.ADDING_PRODUCTS: """太好了！公司基本資料已經收集完成。

現在讓我們來新增產品資料。請依照以下格式提供產品資訊：

產品名稱：[產品名稱]
產品類別：[產品類別]

您可以一次提供一個產品，完成後我會詢問是否還要繼續新增。
如果不需要新增產品，請直接回答「不用」或「完成」。"""
        }

        return prompts.get(field, "請繼續提供資料。")

    def process_message(self, user_message: str) -> tuple[str, bool]:
        """
        Process user message and return bot response
        Returns: (response_message, is_completed)
        """
        # Get conversation history
        history = self.get_conversation_history()

        # Check if this is the first message (no history yet)
        if len(history) == 0:
            # Check for menu selection
            user_msg_lower = user_message.lower().strip()

            # Option 1: Fill in data
            if any(word in user_msg_lower for word in ["1", "填寫", "填写", "開始", "开始"]):
                return "太好了！讓我們開始收集您的公司資料。\n\n" + self.get_prompt_for_field(ConversationState.INDUSTRY), False

            # Option 2: View progress
            elif any(word in user_msg_lower for word in ["2", "進度", "进度", "查看進度"]):
                progress = self.get_progress()
                return f"""📊 資料填寫進度：

已完成欄位：{progress['fields_completed']}/{progress['total_fields']}
產品數量：{progress['products_count']} 個

{self.get_current_data_summary()}

您想繼續填寫資料嗎？（是/否）""", False

            # Option 3: View filled data
            elif any(word in user_msg_lower for word in ["3", "已填", "查看資料", "查看数据"]):
                data_summary = self.get_current_data_summary()
                return f"""📝 目前已填寫的資料：

{data_summary}

您想繼續填寫資料嗎？（是/否）""", False

            # Default: Show menu
            else:
                return self.get_initial_greeting(), False

        # Check if user wants to finish
        if any(word in user_message for word in ["完成", "結束", "不用", "沒有了", "不需要"]):
            # Check if we're in product adding phase
            if any("產品" in msg.content for msg in history[-3:]):
                self.session.status = ChatSessionStatus.COMPLETED
                self.db.commit()

                products_count = len(self.onboarding_data.products)
                return (
                    f"太棒了！您的資料已經收集完成。\n\n"
                    f"✅ 產業別：{self.onboarding_data.industry}\n"
                    f"✅ 資本總額：{self.onboarding_data.capital_amount} 臺幣\n"
                    f"✅ 發明專利數量：{self.onboarding_data.invention_patent_count} 件\n"
                    f"✅ 新型專利數量：{self.onboarding_data.utility_patent_count} 件\n"
                    f"✅ 公司認證數量：{self.onboarding_data.certification_count} 份\n"
                    f"✅ ESG認證：{'有' if self.onboarding_data.esg_certification else '無'}\n"
                    f"✅ 產品數量：{products_count} 個\n\n"
                    f"您可以使用匯出功能來取得完整的JSON格式資料。",
                    True
                )

        # Try to extract product data if we're in product adding phase
        next_field = self.get_next_field_to_collect()

        if next_field == ConversationState.ADDING_PRODUCTS or next_field == ConversationState.COMPLETED:
            product_data = self.extract_product_data(user_message)
            if product_data and product_data.get("product_name"):
                # Valid product data found
                self.add_product(product_data)
                return (
                    f"產品「{product_data.get('product_name')}」已新增成功！\n\n"
                    f"是否要繼續新增其他產品？（如果是，請提供下一個產品資料；如果不是，請回答「完成」）",
                    False
                )

        # Extract and save data for current field
        if next_field and next_field not in [ConversationState.ADDING_PRODUCTS, ConversationState.COMPLETED]:
            success = self.extract_and_save_data(user_message, next_field)

            if not success:
                return f"抱歉，我無法理解您的輸入。{self.get_prompt_for_field(next_field)}", False

            # Get next field to collect
            next_field = self.get_next_field_to_collect()

            if next_field == ConversationState.COMPLETED:
                return "所有資料已收集完成！感謝您的配合。", True

            return self.get_prompt_for_field(next_field), False

        # Default response
        return self.get_prompt_for_field(next_field), False

    def get_progress(self) -> Dict[str, Any]:
        """Get current progress of data collection"""
        fields_completed = 0
        total_fields = 6  # Total number of company fields (excluding registration fields)

        # Only collect fields within chatbot's responsibility
        if self.onboarding_data.industry:
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
