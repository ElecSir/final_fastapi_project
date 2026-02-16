from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class BaseModel(DeclarativeBase):
    # created_at: Mapped[datetime] = mapped_column(default_factory=datetime.now)
    pass
