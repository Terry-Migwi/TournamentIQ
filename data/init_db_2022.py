import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from data.models_2022 import Base
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
Base.metadata.create_all(engine)