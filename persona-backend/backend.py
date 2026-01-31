from flask import Flask ,request
from persona_agent.agent import call_runner
app = Flask(__name__)

@app.route("/health-check")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get('/')
async def handle_query():
    searchParm= request.args.get('q')
    print(searchParm)
    # call the runner function from the above module
    try:
        print("calling runner")
        res=await call_runner(searchParm)
        print(res)
        return res
    except Exception as e :
        print("got some error send message again",e.__cause__)
        return "error occured"