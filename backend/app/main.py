from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.api.v1.airports import router as airports_router



app = FastAPI(title="TripFind API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(airports_router)


@app.get("/api/health")
def get_api_health():
    return {"status": "ok", "message": "TripFind API is running!"}