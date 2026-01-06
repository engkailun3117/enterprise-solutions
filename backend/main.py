from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

from database import get_db, engine, Base
from models import CompanyInfo, User, UserRole, ApplicationStatus, ChatSession, ChatMessage, CompanyOnboarding, Product, ChatSessionStatus
from schemas import (
    CompanyInfoCreate, CompanyInfoResponse,
    UserRegister, UserLogin, TokenResponse, UserResponse, ReviewAction,
    PasswordResetRequest, PasswordResetConfirm,
    ChatMessageCreate, ChatResponse, ChatSessionResponse, ChatMessageResponse,
    OnboardingDataResponse
)
from config import get_settings
from auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_active_user, require_admin
)
from chatbot_handler import ChatbotHandler

# Create database tables
Base.metadata.create_all(bind=engine)

# Debug: Print configuration on startup
settings = get_settings()
print("=" * 60)
print("🔧 Backend Configuration:")
print(f"   Database: {settings.database_url[:30]}...")
print(f"   API Host: {settings.api_host}")
print(f"   API Port: {settings.api_port}")
print(f"   SECRET_KEY: {settings.secret_key[:20]}... (length: {len(settings.secret_key)})")
print("=" * 60)

# Initialize FastAPI app
app = FastAPI(
    title="Supplier Onboarding API",
    description="API for managing supplier company information with authentication and approval workflow",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Nuxt app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Health Check ==============

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Supplier Onboarding API is running",
        "version": "2.0.0",
        "features": ["authentication", "authorization", "approval_workflow"]
    }


# ============== Authentication Endpoints ==============

@app.post("/api/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user account

    - **username**: Unique username (3-50 characters)
    - **email**: Unique email address
    - **password**: Password (minimum 6 characters)

    Returns JWT token and user information
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=UserRole.USER  # Default role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Create access token
        access_token = create_access_token(data={"sub": str(new_user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": new_user.to_dict()
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during registration: {str(e)}"
        )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with username and password

    - **username**: Your username
    - **password**: Your password

    Returns JWT token and user information
    """
    user = authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user information

    Requires: Valid JWT token in Authorization header
    """
    return current_user.to_dict()


@app.post("/api/auth/forgot-password", status_code=status.HTTP_200_OK)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset email

    - **email**: Email address of the user

    Sends a password reset link to the user's email (if account exists)
    Always returns success to prevent email enumeration
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if user:
        # In a real application, you would:
        # 1. Generate a secure reset token
        # 2. Store it in database with expiration time
        # 3. Send email with reset link containing the token
        # For now, we'll just simulate success
        pass

    # Always return success to prevent email enumeration
    return {
        "message": "If the email exists, a password reset link has been sent",
        "email": request.email
    }


@app.post("/api/auth/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Reset password using a reset token

    - **token**: Password reset token
    - **new_password**: New password (minimum 6 characters)

    Resets the user's password if the token is valid
    """
    # In a real application, you would:
    # 1. Verify the reset token
    # 2. Check if it's not expired
    # 3. Find the associated user
    # 4. Update the password
    # For now, this is a placeholder that returns success

    return {
        "message": "Password has been reset successfully"
    }


# ============== Company/Supplier Onboarding Endpoints ==============

@app.post("/api/companies", response_model=CompanyInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company: CompanyInfoCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new supplier onboarding application (ONE TIME ONLY per user)

    - **company_id**: 統一編號 (Unified Business Number) - must be unique
    - **company_name**: 企業名稱 (Company Name)
    - **company_head**: 負責人 (Person in Charge)
    - **company_email**: 聯絡 Email
    - **company_link**: 公司網址 (Company Website) - optional

    Requires: Authentication
    Restriction: Each user can only submit ONE application
    """
    # Check if user already submitted an application
    existing_application = db.query(CompanyInfo).filter(
        CompanyInfo.user_id == current_user.id
    ).first()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted a supplier onboarding application. Only one application per user is allowed."
        )

    try:
        # Create new company record linked to user
        db_company = CompanyInfo(
            Company_ID=company.company_id,
            Company_Name=company.company_name,
            Company_Head=company.company_head,
            Company_Email=company.company_email,
            Company_Link=company.company_link,
            user_id=current_user.id,
            status=ApplicationStatus.PENDING  # Default status
        )

        db.add(db_company)
        db.commit()
        db.refresh(db_company)

        return db_company.to_dict()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with ID {company.company_id} already exists"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating the company: {str(e)}"
        )


@app.get("/api/companies/my-application", response_model=CompanyInfoResponse)
async def get_my_application(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's supplier onboarding application

    Requires: Authentication
    Returns: User's application or 404 if not found
    """
    application = db.query(CompanyInfo).filter(
        CompanyInfo.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not submitted a supplier onboarding application yet"
        )

    return application.to_dict()


@app.get("/api/companies/{company_id}", response_model=CompanyInfoResponse)
async def get_company(
    company_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific company by ID

    - **company_id**: 統一編號 (Unified Business Number)

    Requires: Authentication
    Authorization: Admins can view any application, users can only view their own
    """
    company = db.query(CompanyInfo).filter(CompanyInfo.Company_ID == company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )

    # Authorization check: users can only view their own application
    if current_user.role != UserRole.ADMIN and company.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this application"
        )

    return company.to_dict()


# ============== Admin Endpoints ==============

@app.get("/api/admin/applications", response_model=List[CompanyInfoResponse])
async def get_all_applications(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Retrieve all supplier applications with pagination (ADMIN ONLY)

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    - **status_filter**: Filter by status (pending, approved, rejected) - optional

    Requires: Admin role
    """
    query = db.query(CompanyInfo)

    # Apply status filter if provided
    if status_filter:
        try:
            status_enum = ApplicationStatus(status_filter.lower())
            query = query.filter(CompanyInfo.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status filter. Must be one of: pending, approved, rejected"
            )

    applications = query.offset(skip).limit(limit).all()
    return [app.to_dict() for app in applications]


@app.put("/api/admin/applications/{company_id}/review", response_model=CompanyInfoResponse)
async def review_application(
    company_id: str,
    review: ReviewAction,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Approve or reject a supplier application (ADMIN ONLY)

    - **company_id**: 統一編號 (Unified Business Number)
    - **action**: "approve" or "reject"
    - **rejection_reason**: Required if action is "reject"

    Requires: Admin role
    """
    # Validate action
    if review.action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be either 'approve' or 'reject'"
        )

    # Validate rejection reason
    if review.action == "reject" and not review.rejection_reason:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required when rejecting an application"
        )

    # Find the application
    application = db.query(CompanyInfo).filter(CompanyInfo.Company_ID == company_id).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {company_id} not found"
        )

    # Check if already reviewed
    if application.status != ApplicationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Application has already been {application.status.value}"
        )

    try:
        # Update application status
        if review.action == "approve":
            application.status = ApplicationStatus.APPROVED
            application.rejection_reason = None
        else:
            application.status = ApplicationStatus.REJECTED
            application.rejection_reason = review.rejection_reason

        application.reviewed_by = current_user.id
        application.reviewed_at = datetime.utcnow()

        db.commit()
        db.refresh(application)

        return application.to_dict()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while reviewing the application: {str(e)}"
        )


@app.get("/api/admin/stats")
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get statistics about applications (ADMIN ONLY)

    Returns counts of applications by status

    Requires: Admin role
    """
    total = db.query(CompanyInfo).count()
    pending = db.query(CompanyInfo).filter(CompanyInfo.status == ApplicationStatus.PENDING).count()
    approved = db.query(CompanyInfo).filter(CompanyInfo.status == ApplicationStatus.APPROVED).count()
    rejected = db.query(CompanyInfo).filter(CompanyInfo.status == ApplicationStatus.REJECTED).count()

    return {
        "total_applications": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected
    }


# ============== Chatbot Endpoints ==============

@app.post("/api/chatbot/message", response_model=ChatResponse)
async def send_chatbot_message(
    chat_data: ChatMessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to the onboarding chatbot

    - **message**: User's message to the chatbot
    - **session_id**: Optional session ID to continue an existing conversation

    Requires: Authentication
    Returns: Chatbot response with session information
    """
    try:
        # Initialize chatbot handler
        handler = ChatbotHandler(db, current_user.id, chat_data.session_id)

        # Create new session if needed
        if not handler.session:
            session = handler.create_session()
            # Send welcome message
            welcome_message = (
                "您好！我是企業導入助理 👋\n\n"
                "我將協助您建立公司資料。我會逐步引導您輸入以下資訊：\n"
                "• 公司基本資料（ID、名稱、產業別、國家、地址等）\n"
                "• 公司規模與認證資料\n"
                "• 產品資訊\n\n"
                "讓我們開始吧！首先，請問您的公司ID（統一編號）是什麼？"
            )
            handler.add_message("assistant", welcome_message)

            return ChatResponse(
                session_id=session.id,
                message=welcome_message,
                completed=False,
                progress=handler.get_progress()
            )

        # Save user message
        handler.add_message("user", chat_data.message)

        # Process message and get response
        bot_response, is_completed = handler.process_message(chat_data.message)

        # Save bot response
        handler.add_message("assistant", bot_response)

        return ChatResponse(
            session_id=handler.session.id,
            message=bot_response,
            completed=is_completed,
            progress=handler.get_progress()
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your message: {str(e)}"
        )


@app.get("/api/chatbot/sessions", response_model=List[ChatSessionResponse])
async def get_user_chat_sessions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all chat sessions for the current user

    Requires: Authentication
    Returns: List of user's chat sessions
    """
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(ChatSession.created_at.desc()).all()

    return [session.to_dict() for session in sessions]


@app.get("/api/chatbot/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages for a specific chat session

    - **session_id**: The ID of the chat session

    Requires: Authentication
    Authorization: Users can only view their own sessions
    """
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

    return [msg.to_dict() for msg in messages]


@app.get("/api/chatbot/data/{session_id}", response_model=OnboardingDataResponse)
async def get_onboarding_data(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the onboarding data collected in a chat session

    - **session_id**: The ID of the chat session

    Requires: Authentication
    Authorization: Users can only view their own data
    """
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    onboarding_data = db.query(CompanyOnboarding).filter(
        CompanyOnboarding.chat_session_id == session_id
    ).first()

    if not onboarding_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No onboarding data found for this session"
        )

    return onboarding_data.to_dict()


@app.get("/api/chatbot/export/{session_id}")
async def export_onboarding_data(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export onboarding data in the specified JSON format

    - **session_id**: The ID of the chat session

    Requires: Authentication
    Authorization: Users can only export their own data
    Returns: Data in the Chinese field name format
    """
    # Verify session belongs to user
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    onboarding_data = db.query(CompanyOnboarding).filter(
        CompanyOnboarding.chat_session_id == session_id
    ).first()

    if not onboarding_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No onboarding data found for this session"
        )

    # Return data in export format
    return onboarding_data.to_export_format()


@app.get("/api/chatbot/export/all")
async def export_all_onboarding_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export all completed onboarding data for the current user

    Requires: Authentication
    Returns: Array of all user's completed onboarding data in Chinese field name format
    """
    # Get all completed sessions for user
    completed_sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.status == ChatSessionStatus.COMPLETED
    ).all()

    export_data = []
    for session in completed_sessions:
        onboarding_data = db.query(CompanyOnboarding).filter(
            CompanyOnboarding.chat_session_id == session.id
        ).first()

        if onboarding_data:
            export_data.append(onboarding_data.to_export_format())

    return export_data


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
