import uvicorn
from fastapi import FastAPI

from app.core.config import settings
from app.router import auth_router

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.is_debug)


@app.get("/", tags=["status"], include_in_schema=False)
async def health_check():
    return {"status": "ok"}


app.include_router(auth_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)
