from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///bot_data.db', echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Interaction(Base):
    __tablename__ = 'interactions'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    command = Column(String)
    timestamp = Column(DateTime)
    query = Column(String)
    user_id = Column(Integer)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    language = Column(String)


def create_interaction(chat_id, command, query, user_id, username, first_name, last_name, language):
    interaction_data = {
        'chat_id': chat_id,
        'command': command,
        'timestamp': datetime.now(),
        'query': query,
        'user_id': user_id,
        'username': username,
        'first_name': first_name,
        'last_name': last_name,
        'language': language
    }

    interaction = Interaction(**interaction_data)
    session.add(interaction)
    session.commit()

Base.metadata.create_all(engine)
