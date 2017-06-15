from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
Base = declarative_base()
engine = create_engine('postgresql:///catalog')
DBSession = sessionmaker(bind=engine)
session = DBSession()


class Category(Base):
    __tablename__ = 'category'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250), nullable=False)
    useremail = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'items': [i.serialize for i in session.query(Item)
                      .filter_by(category_id=self.id)
                      .order_by(asc(Item.name)).all()]
        }


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category,
                            backref=backref('item', cascade='all, delete'))
    date_insert = Column(Date)
    useremail = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category.name
        }


Base.metadata.create_all(engine)
