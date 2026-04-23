import uuid
import enum
from datetime import datetime, date
from sqlalchemy import Column, String, Numeric, Date, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class TransactionSource(str, enum.Enum):
    bot = "bot"
    dashboard = "dashboard"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String, default="UZS", nullable=False)
    type = Column(Enum(TransactionType, name="transactiontype"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    date = Column(Date, nullable=False, default=date.today)
    note = Column(Text, nullable=True)
    source = Column(
        Enum(TransactionSource, name="transactionsource"),
        default=TransactionSource.bot,
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
