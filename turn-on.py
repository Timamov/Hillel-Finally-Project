from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def smth():
    return {"status": 2002}