from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import config

engine = create_engine(config.DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)
