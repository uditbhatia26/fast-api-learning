# Creating a simple fastapi app with basic endpoints

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World!!"}

@app.get("/about")
def about():
    return {"message": "Hi My name is Udit"}