from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    ADMIN = "admin"


class ApplicationStatus(str, enum.Enum):
    """Application status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ChatSessionStatus(str, enum.Enum):
    """Chat session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class User(Base):
    """User table for authentication and authorization"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, native_enum=True, create_constraint=True, name='userrole'), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to companies
    companies = relationship("CompanyInfo", back_populates="user", foreign_keys="CompanyInfo.user_id")
    reviewed_companies = relationship("CompanyInfo", back_populates="reviewer", foreign_keys="CompanyInfo.reviewed_by")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CompanyInfo(Base):
    """Company_Info table model with approval workflow"""

    __tablename__ = "Company_Info"

    Company_ID = Column(String(50), primary_key=True, index=True)
    Company_Name = Column(String(100), nullable=False)
    Company_Head = Column(String(80), nullable=False)
    Company_Email = Column(String(50), nullable=False)
    Company_Link = Column(String(200), nullable=True)

    # New fields for authentication and approval workflow
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(ApplicationStatus, native_enum=True, create_constraint=True, name='applicationstatus'), default=ApplicationStatus.PENDING, nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    rejection_reason = Column(String(500), nullable=True)

    # Relationships
    user = relationship("User", back_populates="companies", foreign_keys=[user_id])
    reviewer = relationship("User", back_populates="reviewed_companies", foreign_keys=[reviewed_by])

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "company_id": self.Company_ID,
            "company_name": self.Company_Name,
            "company_head": self.Company_Head,
            "company_email": self.Company_Email,
            "company_link": self.Company_Link,
            "user_id": self.user_id,
            "status": self.status.value,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "rejection_reason": self.rejection_reason
        }


class ChatSession(Base):
    """Chat session table for managing user chatbot conversations"""

    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(ChatSessionStatus, native_enum=True, create_constraint=True, name='chatsessionstatus'),
                    default=ChatSessionStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    onboarding_data = relationship("CompanyOnboarding", back_populates="chat_session", uselist=False)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class ChatMessage(Base):
    """Chat message table for storing conversation history"""

    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class CompanyOnboarding(Base):
    """Company onboarding data collected through chatbot"""

    __tablename__ = "company_onboarding"

    id = Column(Integer, primary_key=True, index=True)
    chat_session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Company Information (主欄)
    company_id = Column(String(100), nullable=True, index=True)  # 公司ID
    company_name = Column(String(200), nullable=True)  # 公司名稱
    industry = Column(String(100), nullable=True)  # 產業別
    country = Column(String(100), nullable=True)  # 國家
    tax = Column(Integer, nullable=True)  # 關稅 (backend only, derived from country)
    address = Column(String(500), nullable=True)  # 地址
    capital_amount = Column(Integer, nullable=True)  # 資本總額(億)
    invention_patent_count = Column(Integer, nullable=True)  # 發明專利數量 - 權重高
    utility_patent_count = Column(Integer, nullable=True)  # 新型專利數量 - 權重低
    certification_count = Column(Integer, nullable=True)  # 公司認證資料數量
    esg_certification = Column(Boolean, nullable=True)  # ESG相關認證資料

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")
    chat_session = relationship("ChatSession", back_populates="onboarding_data")
    products = relationship("Product", back_populates="company_onboarding", cascade="all, delete-orphan")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "chat_session_id": self.chat_session_id,
            "user_id": self.user_id,
            "company_id": self.company_id,
            "company_name": self.company_name,
            "industry": self.industry,
            "country": self.country,
            "tax": self.tax,
            "address": self.address,
            "capital_amount": self.capital_amount,
            "invention_patent_count": self.invention_patent_count,
            "utility_patent_count": self.utility_patent_count,
            "certification_count": self.certification_count,
            "esg_certification": self.esg_certification,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "products": [p.to_dict() for p in self.products] if self.products else []
        }

    def to_export_format(self):
        """Convert to the export JSON format requested by the user"""
        return {
            "公司ID": self.company_id,
            "公司名稱": self.company_name,
            "產業別": self.industry,
            "國家": self.country,
            "關稅": self.tax / 100 if self.tax else None,  # Convert to decimal
            "地址": self.address,
            "資本總額(億)": self.capital_amount,
            "發明專利數量": self.invention_patent_count,
            "新型專利數量": self.utility_patent_count,
            "公司認證資料數量": self.certification_count,
            "ESG相關認證資料": "有" if self.esg_certification else "無",
            "產品": [p.to_export_format() for p in self.products] if self.products else []
        }


class Product(Base):
    """Product information table (子欄)"""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    onboarding_id = Column(Integer, ForeignKey("company_onboarding.id"), nullable=False, index=True)

    # Product Information (子欄)
    product_id = Column(String(100), nullable=True, index=True)  # 產品ID
    product_name = Column(String(200), nullable=True)  # 產品名稱
    price = Column(String(50), nullable=True)  # 價格
    main_raw_materials = Column(String(500), nullable=True)  # 主要原料
    product_standard = Column(String(200), nullable=True)  # 產品規格(尺寸、精度)
    technical_advantages = Column(Text, nullable=True)  # 技術優勢

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    company_onboarding = relationship("CompanyOnboarding", back_populates="products")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "onboarding_id": self.onboarding_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "price": self.price,
            "main_raw_materials": self.main_raw_materials,
            "product_standard": self.product_standard,
            "technical_advantages": self.technical_advantages,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def to_export_format(self):
        """Convert to the export JSON format requested by the user"""
        return {
            "產品ID": self.product_id,
            "產品名稱": self.product_name,
            "價格": self.price,
            "主要原料": self.main_raw_materials,
            "產品規格(尺寸、精度)": self.product_standard,
            "技術優勢": self.technical_advantages
        }
