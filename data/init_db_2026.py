import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from data.models_2026 import Base
from config import DATABASE_URL_2026

engine = create_engine(DATABASE_URL_2026, echo=True)
Base.metadata.create_all(engine)