from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from persona_agent.agent import response_generator
app = FastAPI()
from dotenv import load_dotenv
import os
load_dotenv()
frontend_url = os.getenv("FRONTEND_URL")  # Next.js dev URL


origins = [
   frontend_url
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # allowed domains
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, etc.
    allow_headers=["*"],            # all headers
)
@app.get("/health-check",response_class=HTMLResponse)
async def hello_world():
    return "<p>Hello, World!</p>"

@app.post('/')
async def handle_query(request:Request):
    data = await request.json()
    sessionId= data.get('sessionId')
    query= data.get('query')

    print(sessionId)
    # call the runner function from the above module
    async def event_stream():
        try:
           async for chunk in response_generator(sessionId, query):
                yield f"data: {chunk}\n\n"
        except Exception as e:  
            yield f"\n[ERROR]: {str(e)}\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

