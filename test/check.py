import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # project root

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy import inspect
from database.database import Base, engine  # import engine to connect
import datetime

# -----------------------------
# Define your table/model
# -----------------------------
class SMEAnalysis(Base):
    __tablename__ = "sme_analyses"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, nullable=False)
    business_type = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    financial_metrics = Column(JSON, nullable=False)
    ai_summary = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    report_language = Column(String, nullable=False)

# -----------------------------
# Create table (if not exists) and show info
# -----------------------------
if __name__ == "__main__":
    # create table if it doesn't exist
    Base.metadata.create_all(bind=engine)
    print("Database connected successfully!")

    # inspect tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print("Tables in database:", tables)

    # show columns of your table if it exists
    if "sme_analyses" in tables:
        columns = inspector.get_columns("sme_analyses")
        print("\nColumns in 'sme_analyses':")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
