from sqlalchemy import Column, Integer, Text, SmallInteger, ARRAY, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
import models
Base = declarative_base()


class UserLoverDB(Base):
    __tablename__ = "user_lovers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Text, nullable=False)
    lover_id = Column(Text, nullable=False)
    avatar = Column(Text)
    name = Column(Text, nullable=False)
    gender = Column(SmallInteger, nullable=False)  # 0=男, 1=女
    personality = Column(SmallInteger, nullable=False)
    hobbies = Column(ARRAY(Integer), nullable=False)
    talking_style = Column(SmallInteger, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def toUserLover(self):
        return models.UserLover(
            id=self.id,
            lover_id=self.lover_id,
            user_id=self.user_id,
            avatar=self.avatar,
            name=self.name,
            gender=self.gender,
            personality=self.personality,
            hobbies=self.hobbies,
            talking_style=self.talking_style,
            created_at=self.created_at,
            updated_at=self.updated_at
        )