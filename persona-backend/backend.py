from flask import Flask ,request
from persona_agent.agent import call_runner
from flask_cors import CORS
app = Flask(__name__)
from dotenv import load_dotenv
import os
load_dotenv()
frontend_url = os.getenv("FRONTEND_URL")  # Next.js dev URL
CORS(app, resources={
    r"/*": {
        "origins": [
            
            frontend_url,   # Next.js dev
            
        ]
    }
})

@app.route("/health-check")
def hello_world():
    return "<p>Hello, World!</p>"

@app.post('/')
async def handle_query():
    searchParm= request.args.get('q')
    data = request.get_json()
    sessionId= data.get('sessionId')

    print(sessionId)
    # call the runner function from the above module
    try:
        print("calling runner")
        res=await call_runner(searchParm,sessionId)
        print(res)
        return res
    except Exception as e :
        print("got some error send message again",e)
        return "error occured"