"""
:Description:  ORM数据库映射模型
:Author:  Dexter Lien
:Create:  2020/1/3 16:12
Copyright (c) 2020, Dexter Lien All Rights Reserved.
"""

import sqlalchemy as db
from sqlalchemy import Column
from sqlalchemy.dialects.sqlite import TEXT, CHAR
from sqlalchemy.ext.declarative import declarative_base

engine = db.create_engine('sqlite:///movies.db')
conn = engine.connect()
metadata = db.MetaData()
Base = declarative_base()


class Movie(Base):
    __tablename__ = 'movies'
    uid = Column(CHAR(32), primary_key=True)
    title = Column(TEXT)
    magnets = Column(TEXT)
    infos = Column(TEXT)
    intro = Column(TEXT)


if __name__ == '__main__':
    # 首次运行需要手动创建表
    Base.metadata.create_all(engine)
