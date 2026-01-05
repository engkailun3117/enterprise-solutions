from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
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


class User(Base):
    """User table for authentication and authorization"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, native_enum=True, create_constraint=True, name='userrole'), default=UserRole.USER, nullable=False)
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
