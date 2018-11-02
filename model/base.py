#!/usr/bin/env python
# -*- coding:UTF-8

"""
Created on 2018/10/31

Author: 

Description: 

"""

from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import Column, inspect, Integer, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.schema import MetaData
from sqlalchemy.pool import NullPool

from utiles import config

engine = create_engine(config.get("engine_str"), poolclass=NullPool,
                       connect_args={"use_unicode": True, "charset": "utf8"}, echo=True)


class ModelMixin(object):
    """
    自带id和两个时间戳的base model
    """
    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8",
        "extend_existing": True
    }

    id = Column(Integer, primary_key=True)

    def __getitem__(self, key):
        return getattr(self, key)

    def __getattribute__(self, key):
        return super(ModelMixin, self).__getattribute__(key)

    @classmethod
    def get_first(cls, key, value, session=None):
        obj = session.query(cls).filter(getattr(cls, key) == value).first()
        return obj

    @classmethod
    def get_one(cls, key, value, session=None):
        obj = session.query(cls).filter(getattr(cls, key) == value).one()
        return obj

    @classmethod
    def get_one_or_none(cls, key, value, session=None):
        obj = session.query(cls).filter(getattr(cls, key) == value).one_or_none()
        return obj

    @classmethod
    def get_by_id(cls, value, session):
        obj = session.query(cls).filter_by(id=value).one_or_none()
        return obj

    @classmethod
    def get_all(cls, key=None, value=None, session=None):
        if key:
            objs = session.query(cls).filter(getattr(cls, key) == value).all()
        else:
            objs = session.query(cls).all()
        return objs

    @classmethod
    def merge(cls, obj, key=None, value=None, session=None):
        """
        用返回值来区分更新还是插入
        :param session:
        :param value:
        :param key:
        :param obj:
        """

        if key is None or value is None:
            session.merge(obj)
        else:
            old_obj = cls.get_first(key, value, session)
            if old_obj:
                obj.id = old_obj.id
                obj.update_time = datetime.utcnow()
                session.merge(obj)
            else:
                session.add(obj)
        session.flush()

    def to_dict(self):
        """返回一个dict格式"""
        import builtins
        builtin_types = [t for t in builtins.__dict__.values() if isinstance(t, type)]
        builtin_types.append(datetime)

        result = dict()
        for k in dir(self):
            if not k.startswith('__') and not k.startswith('_') and not callable(k) and hasattr(self, k):
                v = getattr(self, k)
                if v is None or type(v) in builtin_types:
                    result[k] = v
        return result

    @classmethod
    def initialize(cls):
        """删除表并创建表"""
        table_name = cls.__table__.name
        try:
            table = metadata.tables[table_name]
        except KeyError:
            return False
        try:
            metadata.drop_all(tables=[table])
            metadata.create_all(tables=[table])
        except Exception:
            return False
        return True

    @classmethod
    def table_columns(cls):
        """ 得到表的字段 """
        return inspect(cls).columns.keys()

    @classmethod
    def drop_table(cls):
        """删除表"""
        if cls.__table__ in metadata.sorted_tables:
            cls.__table__.drop(engine)

    def save(self, column, session=None):
        flag_modified(self, column)
        session.merge(self)
        session.flush()

    def update_parameter(self, column, session=None):
        if not session:
            session = Session()
        flag_modified(self, column)
        session.merge(self)
        session.flush()


metadata = MetaData(bind=engine)
Entity = declarative_base(name="Entity", metadata=metadata, cls=ModelMixin)


def create_all_table():
    metadata.create_all(checkfirst=True)


def clean_all_table():
    """ 清除所有的表 """
    metadata.drop_all(engine)
    metadata.create_all(engine)


def drop_all_table():
    """ 删除所有的表 """
    metadata.drop_all(engine)


Session = sessionmaker(bind=engine, autocommit=False, autoflush=True, expire_on_commit=False)

@contextmanager
def open_session():
    """ 可以使用with 上下文，在with结束之后自动commit """
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
