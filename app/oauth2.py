from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from . import database, models
from app.schemas import accessToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# create token


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# verify token
def verify_access_token(token: str, credentials_exceptions):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exceptions
        tokenData = accessToken.TokenData(username=username)

        return tokenData
    except JWTError:
        raise credentials_exceptions


# get current user
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):

    credentials_exceptions = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exceptions)  # type:ignore
    user = db.query(models.User).filter(models.User.email == token.username).first()
    return user
