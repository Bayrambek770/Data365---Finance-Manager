import uuid
import string
import random
from datetime import datetime
from sqlalchemy import Column, String, Boolean, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


def generate_unique_code() -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=8))


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    username = Column(String, nullable=True)
    language = Column(String, default="en", nullable=False)
    unique_code = Column(String, unique=True, nullable=False, default=generate_unique_code)
    is_registered = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
