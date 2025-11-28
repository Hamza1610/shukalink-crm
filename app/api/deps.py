from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
from jose import JWTError, jwt
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.security import verify_token
from app.crud.crud_user import crud_user
from app.models.user import User

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)) -> User:
    """
    Get current user from JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        phone_number: str = payload.get("phone_number")
        
        if user_id is None:
            raise credentials_exception
        
        token_data = {"user_id": user_id, "phone_number": phone_number}
    except JWTError:
        raise credentials_exception
    
    user = crud_user.get(db, id=user_id)
    if user is None:
        raise credentials_exception
    
    # Update last active timestamp
    user.last_active = datetime.utcnow()
    db.add(user)
    db.commit()
    
    return user