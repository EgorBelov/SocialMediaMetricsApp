from sqlalchemy import create_engine, Column, Integer, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()
from sqlalchemy.orm import sessionmaker


class GraphData(Base):
    __tablename__ = 'graph_data'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    data = Column(JSONB)