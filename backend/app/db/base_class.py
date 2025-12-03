# app/db/base_class.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
import uuid

Base = declarative_base()

def generate_uuid():
    return uuid.uuid4().hex