from fastapi import FastAPI

app = FastAPI(
    title="Insurance Claims Triage Assistant",
    version="0.1.0",
    description="Minimal scaffold for the M9 Capstone project.",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "insurance-claims-triage-assistant",
    }


@app.get("/")
def root():
    return {
        "message": "Insurance Claims Triage Assistant API is running."
    }
