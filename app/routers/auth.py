from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from .. import database, models, util, oauth2
from app.schemas import accessToken, user
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(tags=["authentication"])


@router.post(
    "/signup", response_model=user.SignUpModel, status_code=status.HTTP_201_CREATED
)
async def sign_up(user: user.SignUpModel, db: Session = Depends(database.get_db)):

    hashed_password = util.get_password_hash(user.password)
    user.password = hashed_password
    new_user_exists = (
        db.query(models.User).filter(models.User.email == user.email).first()
    )

    if new_user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"{user.email} already exists"
        )
    new_user = models.User(**user.model_dump())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):

    user = (
        db.query(models.User)
        .filter(models.User.email == user_credentials.username)
        .first()
    )

    if not user or not util.verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="invalid credentials"
        )

    # if valid credentials, create token

    access_token = oauth2.create_access_token(data={"sub": user.email})
    tokenData = accessToken.Token(access_token=access_token, token_type="bearer")
    return tokenData
