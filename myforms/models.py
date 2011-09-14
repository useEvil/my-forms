import logging
import transaction
import datetime as date

from sqlalchemy import Column, Numeric, Integer, String, ForeignKey, Sequence, Unicode, select, func, desc, asc, distinct, not_

from sqlalchemy.types import DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation, backref
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from zope.sqlalchemy import ZopeTransactionExtension

from myforms.helpers import *

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
Log  = logging.getLogger(__name__)

class TwitterStatus(Base):
    """
    DROP TABLE TWITTER_STATUS;
    CREATE TABLE TWITTER_STATUS
    (
        ID          NUMBER(2) NOT NULL,
        STATUS      VARCHAR2(140) NOT NULL,
        HASHTAGS    VARCHAR2(2000) NULL,
        MENTIONS    VARCHAR2(2000) NULL,
        CONSTRAINT PK_TWITTER_STATUS PRIMARY KEY (ID)
    );
    """
    __tablename__ = 'TWITTER_STATUS'

    id       = Column('ID', Integer, primary_key=True)
    status   = Column('STATUS', Unicode(255), nullable=False)
    hashtags = Column('HASHTAGS', Unicode(2000), nullable=True)
    mentions = Column('MENTIONS', Unicode(2000), nullable=True)

    def getById(self, id=None):
        if not id: return
        result = DBSession().query(self.__class__).filter(self.__class__.id==id).one()
        return result

    def getAll(self):
        results = DBSession().query(self.__class__).all()
        return results


class HundredPushups(Base):
    """
    DROP TABLE HUNDRED_PUSHUPS;
    CREATE TABLE HUNDRED_PUSHUPS
    (
        ID              NUMBER(2) NOT NULL,
        WEEK            NUMBER(2) NOT NULL,
        DAY             NUMBER(2) NOT NULL,
        LEVEL           NUMBER(2) NOT NULL,
        SET1            NUMBER(2) NULL,
        SET2            NUMBER(2) NULL,
        SET3            NUMBER(2) NULL,
        SET4            NUMBER(2) NULL,
        EXHAUST         NUMBER(2) NOT NULL,
        HASHTAGS        VARCHAR2(2000) NULL,
        MENTIONS        VARCHAR2(2000) NULL,
        PERMALINK       VARCHAR2(2000) NULL,
        MESSAGE         VARCHAR2(2000) NULL,
        CREATED_DATE    DATE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        CONSTRAINT PK_RELEASE_TYPE PRIMARY KEY (ID)
    );
    """
    __tablename__ = 'HUNDRED_PUSHUPS'

    id          = Column('ID', Integer, primary_key=True)
    week        = Column('WEEK', Integer, nullable=False)
    day         = Column('DAY', Integer, nullable=False)
    level       = Column('LEVEL', Integer, nullable=False)
    set1        = Column('SET1', Integer, nullable=True)
    set2        = Column('SET2', Integer, nullable=True)
    set3        = Column('SET3', Integer, nullable=True)
    set4        = Column('SET4', Integer, nullable=True)
    exhaust     = Column('EXHAUST', Integer, nullable=False)
    hashtags    = Column('HASHTAGS', Unicode(2000), nullable=True)
    mentions    = Column('MENTIONS', Unicode(2000), nullable=True)
    permalink   = Column('PERMALINK', Unicode(2000), nullable=False)
    message     = Column('MESSAGE', Unicode(2000), nullable=False)
    createdDate = Column('CREATED_DATE', DateTime, nullable=False)

    def getById(self, id=None):
        if not id: return
        result = DBSession().query(self.__class__).filter(self.__class__.id==id).one()
        return result

    def getByCreatedDate(self, startDate=None, endDate=None, filter=None, type=None):
        query = DBSession().query(self.__class__)
        if filter:
            for word in filter.split():
                query = query.filter(getattr(Message, type).ilike("%%%s%%" % word))
        return query.filter(self.__class__.createdDate>=startDate).filter(self.__class__.createdDate<=endDate).order_by(desc(self.__class__.createdDate), desc(self.__class__.id)).all()

    def getAll(self):
        results = DBSession().query(self.__class__).all()
        return results

    def getAll(self, filter=None, type=None):
        query = DBSession().query(self.__class__)
        if filter:
            for word in filter.split():
                query = query.filter(getattr(Release, type).ilike("%%%s%%" % word))
        try:
            list = query.order_by(desc(self.__class__.createdDate), desc(self.__class__.id)).all()
        except NoResultFound:
            list = [ ]
        return list

    def getRecent(self):
        try:
            result = DBSession().query(self.__class__).order_by(desc(self.__class__.createdDate), desc(self.__class__.id)).limit(1).offset(0).one()
        except:
            result = DBSession()
            result.week  = 0
            result.day   = 0
            result.level = 0
            result.set1  = 0
            result.set2  = 0
            result.set3  = 0
            result.set4  = 0
            result.exhaust   = 0
            result.mentions  = None
            result.permalink = None
            result.message   = None
            result.hashtags  = '#100Pushups'
        return result

    def getSet(self, limit=10, offset=0):
        return DBSession().query(self.__class__).order_by(desc(self.__class__.createdDate), desc(self.__class__.id)).limit(limit).offset(offset).all()

    def getTotal(self):
        return DBSession().query(self.__class__).count()

    def setParams(self, params):
        for attr in params.keys():
            value = params.get(attr)
            if attr == 'createdDate' and value:
                value = date.datetime.strptime(value, getSettings('date.short'))
            else:
                if value: setattr(self, attr, value)
        if not self.createdDate:
            self.createdDate = date.datetime.today()

    def total(self):
        return int(self.set1)+int(self.set2)+int(self.set3)+int(self.set4)+int(self.exhaust)

    def create(self, params):
        self.setParams(params)
        session = DBSession()
        session.add(self)
        return

    def update(self, params):
        self.setParams(params)
        session = DBSession()
        return

    def delete(self):
        session = DBSession()
        session.delete(self)
        return


## For Testing Framework ##
class MyModel(Base):
    __tablename__ = 'models'
    id    = Column(Integer, primary_key=True)
    name  = Column(Unicode(255), unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
