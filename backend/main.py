from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.api.routes import router
app=FastAPI(title="SciTutor Workbench API",version="3.1.0")
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=False,allow_methods=["GET","POST"],allow_headers=["*"])
app.include_router(router,prefix="/api/v3")
@app.get("/health")
def health(): return {"status":"ok","service":"scitutor-api"}
