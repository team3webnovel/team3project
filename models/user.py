from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)  # 아이디 (고유)
    email = Column(String(100), unique=True, nullable=False)     # 이메일 (고유)
    password = Column(String(255), nullable=False)               # 비밀번호
    created_at = Column(TIMESTAMP, server_default=func.now())    # 생성 시간 (자동)

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, email={self.email})>"