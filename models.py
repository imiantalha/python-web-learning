from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    