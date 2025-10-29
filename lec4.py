from fastapi import FastAPI, Path, HTTPException, Query
from typing import List, Literal
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

@app.get("/view")
def view():
    data = load_data("patients.json")
    return data

@app.get("/patient/{patient_id}")
def get_patient(patient_id: str = Path(...,description="Id of the patient")):
    data = load_data("patients.json")
    if patient_id in data:
        return data[patient_id]
    else:
        raise HTTPException(status_code=404, detail="Patient Id not found")


@app.get("/sort")
def sort_patient(sort_by : Literal['weight', 'bmi', 'age', 'height'] = Query(..., description="Sort on the basis of height, weight, or bmi"), order: Literal['asc', 'desc'] = Query(default='asc', description="Choose the order between asc or desc")):

    valid_fields = ["height", "bmi", "weight"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field, select from {valid_fields}")
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail=f"Invalid order, select from asc or desc")
    

    data = load_data("patients.json")
    sort_order = False if order == 'asc' else True
    sorted_data = sorted(data.values(), key=lambda x : x.get(sort_by, 0), reverse=sort_order)
    return sorted_data
