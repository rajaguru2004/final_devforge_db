import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"
from fastapi import FastAPI
from app.routers import nodes, edges, search, pdf

app = FastAPI(title="Hybrid Retrieval System")

app.include_router(nodes.router)
app.include_router(edges.router)
app.include_router(search.router)
app.include_router(pdf.router)

@app.get("/")
def root():
    return {"message": "Hybrid Retrieval System API is running"}
