from fastapi import FastAPI
from pydantic import BaseModel, conlist
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# FastAPI app
app = FastAPI()

# PostgreSQL connection URL
DATABASE_URL = os.environ.get("DATABASE_URL")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model for the device data
class DeviceData(Base):
    __tablename__ = "device_data"

    id = Column(Integer, primary_key=True, index=True)
    imei = Column(String, index=True)
    timestamp = Column(DateTime)

    temperature_1 = Column(Float)
    temperature_2 = Column(Float)
    temperature_3 = Column(Float)
    temperature_4 = Column(Float)

    humidity_1 = Column(Float)
    humidity_2 = Column(Float)
    humidity_3 = Column(Float)
    humidity_4 = Column(Float)

    rssi_1 = Column(Integer)
    rssi_2 = Column(Integer)
    rssi_3 = Column(Integer)
    rssi_4 = Column(Integer)

    battery = Column(Float)
# Create the table
Base.metadata.create_all(bind=engine)

# Pydantic models
class Payload(BaseModel):
    temperature: conlist(float, min_length=4, max_length=4)
    humidity: conlist(float, min_length=4, max_length=4)
    rssi: conlist(int, min_length=4, max_length=4)
    battery: float

class DevicePayload(BaseModel):
    imei: str
    timestamp: datetime
    payload: Payload

# FastAPI endpoint to receive data
@app.post("/ingest")
async def ingest_data(data: DevicePayload):
    db = SessionLocal()
    try:
        new_entry = DeviceData(
            imei=data.imei,
            timestamp=data.timestamp,

            temperature_1=data.payload.temperature[0],
            temperature_2=data.payload.temperature[1],
            temperature_3=data.payload.temperature[2],
            temperature_4=data.payload.temperature[3],

            humidity_1=data.payload.humidity[0],
            humidity_2=data.payload.humidity[1],
            humidity_3=data.payload.humidity[2],
            humidity_4=data.payload.humidity[3],

            rssi_1=data.payload.rssi[0],
            rssi_2=data.payload.rssi[1],
            rssi_3=data.payload.rssi[2],
            rssi_4=data.payload.rssi[3],

            battery=data.payload.battery
        )
        db.add(new_entry)
        db.commit()
        return {"status": "success", "message": "Data stored"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
