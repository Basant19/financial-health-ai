# test/test_database.py
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# -----------------------------
# Add project root to path so "backend" can be imported
# -----------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.database import Base
from backend.models.models import SMEAnalysis

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing database connection with URL: {DATABASE_URL}")

# -----------------------------
# Create engine
# -----------------------------
engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL logs

# -----------------------------
# Create tables
# -----------------------------
print("Creating tables if they do not exist...")
Base.metadata.create_all(bind=engine)
print("Tables creation complete!")

# -----------------------------
# Inspect database
# -----------------------------
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables in database:", tables)

# -----------------------------
# Insert a test record
# -----------------------------
Session = sessionmaker(bind=engine)
session = Session()

print("Inserting a test SME record...")
test_sme = SMEAnalysis(
    business_name="Test SME",
    business_type="Retail",
    financial_metrics={"revenue": 10000, "expenses": 5000},
    ai_summary="Healthy business with positive cash flow",
    risk_level="Low"
)

session.add(test_sme)
session.commit()
print("Test SME record inserted successfully!")

# -----------------------------
# Query back the record
# -----------------------------
print("Querying SME records...")
sme_records = session.query(SMEAnalysis).all()
for record in sme_records:
    print(record)

session.close()
print("Database test completed successfully!")
