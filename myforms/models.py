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
        SET5            NUMBER(2) NULL,
        SET6            NUMBER(2) NULL,
        SET7            NUMBER(2) NULL,
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
    set5        = Column('SET5', Integer, nullable=True)
    set6        = Column('SET6', Integer, nullable=True)
    set7        = Column('SET7', Integer, nullable=True)
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
            result.set5  = 0
            result.set6  = 0
            result.set7  = 0
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
        return int(self.set1)+int(self.set2)+int(self.set3)+int(self.set4)+int(self.set5)+int(self.set6)+int(self.set7)+int(self.exhaust)

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
class Fundraiser(Base):
    """
    DROP TABLE FUNDRAISER;
    CREATE TABLE FUNDRAISER
    (
        ID              NUMBER(2) NOT NULL,
        NAME            VARCHAR2(2000) NULL,
        CANDY1          NUMBER(2) NULL DEFAULT 0,
        CANDY2          NUMBER(2) NULL DEFAULT 0,
        CANDY3          NUMBER(2) NULL DEFAULT 0,
        CANDY4          NUMBER(2) NULL DEFAULT 0,
        CANDY5          NUMBER(2) NULL DEFAULT 0,
        CANDY6          NUMBER(2) NULL DEFAULT 0,
        CANDY7          NUMBER(2) NULL DEFAULT 0,
        CANDY8          NUMBER(2) NULL DEFAULT 0,
        CANDY9          NUMBER(2) NULL DEFAULT 0,
        CANDY10         NUMBER(2) NULL DEFAULT 0,
        CANDY11         NUMBER(2) NULL DEFAULT 0,
        CANDY12         NUMBER(2) NULL DEFAULT 0,
        CANDY13         NUMBER(2) NULL DEFAULT 0,
        CREATED_DATE    DATE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        CONSTRAINT PK_RELEASE_TYPE PRIMARY KEY (ID)
    );
    """
    __tablename__ = 'FUNDRAISER'

    id          = Column('ID', Integer, primary_key=True)
    name        = Column('NAME', Unicode(2000), nullable=True)
    candy1      = Column('CANDY1', Integer, nullable=True, default=0)
    candy2      = Column('CANDY2', Integer, nullable=True, default=0)
    candy3      = Column('CANDY3', Integer, nullable=True, default=0)
    candy4      = Column('CANDY4', Integer, nullable=True, default=0)
    candy5      = Column('CANDY5', Integer, nullable=True, default=0)
    candy6      = Column('CANDY6', Integer, nullable=True, default=0)
    candy7      = Column('CANDY7', Integer, nullable=True, default=0)
    candy8      = Column('CANDY8', Integer, nullable=True, default=0)
    candy9      = Column('CANDY9', Integer, nullable=True, default=0)
    candy10     = Column('CANDY10', Integer, nullable=True, default=0)
    candy11     = Column('CANDY11', Integer, nullable=True, default=0)
    candy12     = Column('CANDY12', Integer, nullable=True, default=0)
    candy13     = Column('CANDY13', Integer, nullable=True, default=0)
    total       = Column('TOTAL', Integer, nullable=False, default=0)
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

    def getGraphingData(self):
        q = DBSession().query(
                func.sum(Fundraiser.candy1).label('total_candy1'),
                func.sum(Fundraiser.candy2).label('total_candy2'),
                func.sum(Fundraiser.candy3).label('total_candy3'),
                func.sum(Fundraiser.candy4).label('total_candy4'),
                func.sum(Fundraiser.candy5).label('total_candy5'),
                func.sum(Fundraiser.candy6).label('total_candy6'),
                func.sum(Fundraiser.candy7).label('total_candy7'),
                func.sum(Fundraiser.candy8).label('total_candy8'),
                func.sum(Fundraiser.candy9).label('total_candy9'),
                func.sum(Fundraiser.candy10).label('total_candy10'),
                func.sum(Fundraiser.candy11).label('total_candy11'),
                func.sum(Fundraiser.candy12).label('total_candy12'),
                func.sum(Fundraiser.candy13).label('total_candy13'),
                Fundraiser.createdDate,
        )
        q = q.group_by(Fundraiser.createdDate)
        return q.all()

    def total_price(self):
        total =  (self.candy1  * 18.9)
        total += (self.candy2  * 16.5)
        total += (self.candy3  * 16.5)
        total += (self.candy4  * 16.5)
        total += (self.candy5  * 16.5)
        total += (self.candy6  * 16.5)
        total += (self.candy7  * 15.9)
        total += (self.candy8  * 8.25)
        total += (self.candy9  * 8.25)
        total += (self.candy10 * 15.8)
        total += (self.candy11 * 6.50)
        total += (self.candy12 * 6.50)
        total += (self.candy13 * 16.5)
        return price(total)

    def create(self, params):
        self.setParams(params)
        session = DBSession()
        session.add(self)
        return

    def setParams(self, params):
        for attr in params.keys():
            value = params.get(attr)
            if attr == 'createdDate' and value:
                value = date.datetime.strptime(value, getSettings('date.short'))
            else:
                if value: setattr(self, attr, value)
        if not self.createdDate:
            self.createdDate = date.datetime.today()

    def getTotals(self, orders, attr):
        total = 0
        for order in orders:
            value = getattr(order, attr)
            total += value
        return total


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
