from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base

Base = declarative_base()
from sqlalchemy.orm import sessionmaker



class GraphData(Base):
    __tablename__ = 'graph_data'
    id = Column(Integer, primary_key=True)
    data = Column(JSONB)

#
# database="SocialMediaMetrics",
# user="postgres",
# password="123321",
# host="localhost",
# port="5432"
# Создание подключения к базе данных
engine = create_engine('postgresql://postgres:123321@localhost:5432/SocialMediaMetrics')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# JSON-данные для сохранения
json_data = {
    "nodes": [
        {"name": "Myriel", "group": 1, "photo": "path"},
        {"name": "Napoleon", "group": 1, "photo": "path"},
        {"name": "Mlle.Baptistine", "group": 1, "photo": "path"}
    ],
    "links": [
        {"source": 1, "target": 0, "value": 1},
        {"source": 2, "target": 0, "value": 8}
    ]
}

# Создание объекта и сохранение данных в базу
graph_data = GraphData(data=json_data)
session.add(graph_data)
session.commit()
