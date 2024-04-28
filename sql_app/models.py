import datetime

from sqlalchemy import TIMESTAMP, Column, Integer, String

from .database import Base


class User(Base):
    '''
    SQLAlchemy table for users.

    'created_at' field is set upon creation.
    '''

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    created_at = Column(TIMESTAMP, default=datetime.datetime.now)
    login = Column(String)
    password = Column(String)
    project_id = Column(Integer)
    env = Column(String)
    domain = Column(String)
    locktime = Column(TIMESTAMP)
