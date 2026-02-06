# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.analysis import router as analysis_router
from backend.routes.report import router as report_router
from backend.utils.logger import get_logger
from backend.utils.exceptions import CustomException

# ----------------------------------
# Logger setup
# ----------------------------------
logger = get_logger("MainApp")

# ----------------------------------
# FastAPI app setup
# ----------------------------------
app = FastAPI(
    title="Financial Health Assessment API",
    description="AI-assisted financial health analysis for SMEs",
    version="1.0.0"
)

# ----------------------------------
# Enable CORS (for frontend integration)
# ----------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------
# Register routes
# ----------------------------------
try:
    app.include_router(analysis_router)
    app.include_router(report_router)
    logger.info("API routes registered successfully")
except Exception as e:
    logger.exception("Failed to register API routes")
    raise CustomException(f"Route registration failed: {str(e)}")

# ----------------------------------
# Root endpoint
# ----------------------------------
@app.get("/")
def root():
    logger.debug("Root endpoint accessed")
    return {"status": "ok", "message": "Financial Health Assessment API running"}
