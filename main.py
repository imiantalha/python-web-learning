
from fastapi import Depends, FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User

app = FastAPI(title="User Management API")

# Create tables for this learning project.
Base.metadata.create_all(bind=engine)


# Request and response schemas
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(gt=0, le=120)
    is_active: bool = True


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    age: int | None = Field(default=None, gt=0, le=120)
    is_active: bool | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    age: int
    is_active: bool


# CREATE
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
):
    user = User(**data.model_dump())

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A user with this email may already exist",
        )

    return user


# READ ALL
@app.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(User).order_by(User.id)).all()


# READ ONE
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# UPDATE PARTIALLY
@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(status_code=400, detail="No fields provided")

    if any(value is None for value in changes.values()):
        raise HTTPException(
            status_code=422,
            detail="Fields cannot be null",
        )

    for field, value in changes.items():
        if field == "email":
            value = str(value)

        setattr(user, field, value)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A user with this email may already exist",
        )

    return user


# DELETE
@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return Response(status_code=204)
