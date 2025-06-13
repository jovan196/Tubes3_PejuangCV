from sqlalchemy import create_engine, Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class ApplicantProfile(Base):
    __tablename__ = 'ApplicantProfile'
    applicant_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), default=None)
    last_name = Column(String(50), default=None)
    date_of_birth = Column(Date, default=None)
    address = Column(String(255), default=None)
    phone_number = Column(String(20), default=None)
    applications = relationship('ApplicationDetail', back_populates='profile')

class ApplicationDetail(Base):
    __tablename__ = 'ApplicationDetail'
    detail_id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey('ApplicantProfile.applicant_id'), nullable=False)
    application_role = Column(String(100), default=None)
    cv_path = Column(Text)
    profile = relationship('ApplicantProfile', back_populates='applications')


def get_engine(db_path: str = 'ats.db'):
    """
    Create a SQLite engine pointing to the given file path.
    """
    engine = create_engine(f'sqlite:///{db_path}', connect_args={'check_same_thread': False})
    return engine


def init_db(engine):
    Base.metadata.create_all(engine)


def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()