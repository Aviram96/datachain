from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, get_db
from sqlalchemy.orm import Session
import models

# Create database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Datachain API", version="1.0")

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and DB connection."""
    # Simple query to ensure DB is responsive
    db.execute("SELECT 1")
    return {"status": "ok", "message": "Datachain API is running locally."}