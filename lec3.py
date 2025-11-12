# Added a get request to get the data of a specific file

from fastapi import FastAPI
import json

app = FastAPI()

@app.get('/')
def home():
    return {"message": "Patient Management System API!"}

@app.get('/about')
def about():
    return {"message": "A fully functional API to access patients data"}


def load_data(file_path):
    with open(f"{file_path}", "r") as file:
        data = json.load(file)
        return data

@app.get('/view')
def view():
    data = load_data("patients.json")
    return data