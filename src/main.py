# src/main.py
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.CRUDdb import router as crud_router  # Import CRUD router

app = FastAPI()

# Set up CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins (you can use ["*"] for all)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the CRUD router
app.include_router(crud_router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
