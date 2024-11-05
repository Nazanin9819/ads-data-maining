from sqlalchemy import Boolean, Column, ForeignKey, Integer, String,DateTime,Enum,Float,Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .database import Base
from geoalchemy2 import Geometry

class SSP(Base):
    __tablename__ = "ssp"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    ssp_id = Column(String(128))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SSP_REQUEST(Base):
    __tablename__ = "ssp_request"

    id = Column(Integer, primary_key=True)
    ssp_id = Column(Integer, ForeignKey("ssp.id"))
    bid_floor = Column(String(128))
    time_max = Column(String(128))
    country = Column(String(128))
    city = Column(String(128))
    zip_code = Column(String(128))
    app_version = Column(String(128))
    app_name = Column(String(128))
    app_bundle = Column(String(500))
    app_keywords = Column(String(500))
    app_store_url = Column(String(2500))
    device_make = Column(String(128))
    device_model = Column(String(128))
    device_carrier = Column(String(128))
    device_user_agent = Column(Text)
    device_ip = Column(String(128))
    device_os = Column(String(128))
    device_os_version = Column(String(128))
    location = Column(Geometry('POINT'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    ssp_info = relationship("SSP", lazy='joined')

class SSP_RESPONSE(Base):
    __tablename__ = "ssp_response"

    id = Column(Integer, primary_key=True)
    ssp_id = Column(Integer, ForeignKey("ssp.id"))
    ssp_response_id = Column(String(500))
    height = Column(Integer)
    weight = Column(Integer)
    price = Column(Float)
    domain= Column(String(500))
    url= Column(String(5000))
    currency= Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    ssp_info = relationship("SSP", lazy='joined')

class DSP(Base):
    __tablename__ = "dsp"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    dsp_id = Column(String(128))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class DSP_REQUEST(Base):
    __tablename__ = "dsp_request"

    id = Column(Integer, primary_key=True)
    dsp_id = Column(Integer, ForeignKey("dsp.id"))
    bid_floor = Column(String(128))
    time_max = Column(String(128))
    country = Column(String(128))
    city = Column(String(128))
    zip_code = Column(String(128))
    app_version = Column(String(128))
    app_name = Column(String(128))
    app_bundle = Column(String(500))
    app_keywords = Column(String(500))
    app_store_url = Column(String(2500))
    device_make = Column(String(128))
    device_model = Column(String(128))
    device_carrier = Column(String(128))
    device_user_agent = Column(Text)
    device_ip = Column(String(128))
    device_os = Column(String(128))
    device_os_version = Column(String(128))
    location = Column(Geometry('POINT'))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    dsp_info = relationship("DSP", lazy='joined')

class DSP_RESPONSE(Base):
    __tablename__ = "dsp_response"

    id = Column(Integer, primary_key=True)
    dsp_id = Column(Integer, ForeignKey("dsp.id"))
    dsp_response_id = Column(String(500))
    height = Column(Integer)
    weight = Column(Integer)
    price = Column(Float)
    domain= Column(String(500))
    url= Column(String(5000))
    currency= Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    dsp_info = relationship("DSP", lazy='joined')