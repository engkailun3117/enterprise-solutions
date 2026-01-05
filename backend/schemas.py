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
