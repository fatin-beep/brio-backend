from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.whatsapp import router as whatsapp_router
from routes.dashboard import router as dashboard_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="BRIO Backend")

# CORS — allows Usman's Vercel frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://neuraflux.io",
        "https://brio.neuraflux.io",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WhatsApp routes
app.include_router(whatsapp_router, prefix="/api")

# Dashboard routes
app.include_router(dashboard_router, prefix="/api")


# Health check
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "BRIO Backend"}


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"⚠️ Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "detail": "Internal server error"}
    )