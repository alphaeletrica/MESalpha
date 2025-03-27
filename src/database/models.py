from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Machine(Base):
    __tablename__ = 'machines'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    model = Column(String)
    status = Column(String)
    efficiency = Column(Float)
    uptime = Column(Float)
    maintenance_schedule = Column(DateTime)
    processes = relationship("Process", back_populates="machine")

class Process(Base):
    __tablename__ = 'processes'
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey('machines.id'))
    product_code = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    quality_score = Column(Float)
    defects = Column(Integer)
    machine = relationship("Machine", back_populates="processes")
