from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ============== Authentication Schemas ==============

class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., max_length=100, description="Email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "secure_password123"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "secure_password123"
            }
        }


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    username: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="Email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=6, max_length=100, description="New password")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset_token_here",
                "new_password": "new_secure_password123"
            }
        }


# ============== Company Schemas ==============

class CompanyInfoCreate(BaseModel):
    """Schema for creating a new company record"""

    company_id: str = Field(..., max_length=50, description="統一編號 (Unified Business Number)")
    company_name: str = Field(..., max_length=100, description="企業名稱 (Company Name)")
    company_head: str = Field(..., max_length=80, description="負責人 (Person in Charge)")
    company_email: EmailStr = Field(..., max_length=50, description="聯絡 Email")
    company_link: Optional[str] = Field(None, max_length=200, description="公司網址 (Company Website)")

    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "23456789",
                "company_name": "智群科技股份有限公司",
                "company_head": "林小明",
                "company_email": "sales@accton.com",
                "company_link": "https://www.accton.com"
            }
        }


class CompanyInfoResponse(BaseModel):
    """Schema for company info response"""

    company_id: str
    company_name: str
    company_head: str
    company_email: str
    company_link: Optional[str]
    user_id: int
    status: str
    reviewed_by: Optional[int]
    reviewed_at: Optional[datetime]
    created_at: datetime
    rejection_reason: Optional[str]

    class Config:
        from_attributes = True


class ReviewAction(BaseModel):
    """Schema for reviewing an application"""
    action: str = Field(..., description="Action to take: 'approve' or 'reject'")
    rejection_reason: Optional[str] = Field(None, max_length=500, description="Reason for rejection (required if action is 'reject')")

    class Config:
        json_schema_extra = {
            "example": {
                "action": "approve"
            }
        }


# ============== Chatbot Schemas ==============

class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    message: str = Field(..., min_length=1, description="User's message")
    session_id: Optional[int] = Field(None, description="Session ID (if continuing an existing session)")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "我想要開始設定我的公司資料",
                "session_id": None
            }
        }


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Schema for chatbot response"""
    session_id: int
    message: str
    completed: bool = False
    progress: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1,
                "message": "您好！我是企業導入助理。我將協助您建立公司資料。首先，請問您的公司名稱是什麼？",
                "completed": False,
                "progress": {
                    "company_info_complete": False,
                    "products_complete": False
                }
            }
        }


class ChatSessionResponse(BaseModel):
    """Schema for chat session response"""
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProductData(BaseModel):
    """Schema for product data"""
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    price: Optional[str] = None
    main_raw_materials: Optional[str] = None
    product_standard: Optional[str] = None
    technical_advantages: Optional[str] = None


class CompanyOnboardingData(BaseModel):
    """Schema for company onboarding data"""
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    industry: Optional[str] = None
    country: Optional[str] = None
    tax: Optional[int] = None
    address: Optional[str] = None
    capital_amount: Optional[int] = None
    invention_patent_count: Optional[int] = None
    utility_patent_count: Optional[int] = None
    certification_count: Optional[int] = None
    esg_certification: Optional[bool] = None
    products: list[ProductData] = []


class OnboardingDataResponse(BaseModel):
    """Schema for onboarding data response"""
    id: int
    chat_session_id: int
    user_id: int
    company_id: Optional[str]
    company_name: Optional[str]
    industry: Optional[str]
    country: Optional[str]
    tax: Optional[int]
    address: Optional[str]
    capital_amount: Optional[int]
    invention_patent_count: Optional[int]
    utility_patent_count: Optional[int]
    certification_count: Optional[int]
    esg_certification: Optional[bool]
    created_at: datetime
    updated_at: datetime
    products: list[dict]

    class Config:
        from_attributes = True


class SubmitChatbotApplicationRequest(BaseModel):
    """Schema for submitting chatbot data as company application"""
    session_id: Optional[int] = Field(None, description="Chat session ID (defaults to latest active session)")
    company_head: Optional[str] = Field(None, max_length=80, description="負責人 (Person in Charge) - defaults to username")
    company_email: Optional[EmailStr] = Field(None, max_length=50, description="聯絡 Email - defaults to user email")
    company_link: Optional[str] = Field(None, max_length=200, description="公司網址 (Company Website)")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": 1,
                "company_head": "林小明",
                "company_email": "contact@company.com",
                "company_link": "https://www.company.com"
            }
        }
