from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.agent import run_agent

# FastAPI application

app = FastAPI(
    title="Fonada AI Support Agent",
    description=(
        "AI support agent using Python, FastAPI, "
        "LLM and MCP."
    ),
    version="1.0.0"
)


# Request model

class ChatRequest(BaseModel):

    message: str


# Root

@app.get("/")
async def root():

    return {
        "application": "Fonada AI Support Agent",
        "status": "running"
    }


# Health check

@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


# Chat endpoint

@app.post("/chat")
async def chat(request: ChatRequest):

    if not request.message.strip():

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    try:

        response = await run_agent(
            request.message
        )

        return {
            "success": True,
            "response": response
        }

    except Exception as error:

       raise HTTPException(
            status_code=500,
            detail=str(error))

