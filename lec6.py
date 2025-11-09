from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, AnyHttpUrl, computed_field
from typing import List, Literal, Annotated, Optional
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient")]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="City where the user lives")]
    age: Annotated[int, Field(..., description="Current Age of the User", gt=0)]
    gender: Annotated[Literal["Male", "Female"], Field(..., description="Gender of the user")]
    height: Annotated[float, Field(..., description="Height of the user")]
    weight: Annotated[int, Field(..., description="Weight of the user", gt=0)]

    @computed_field
    def bmi(self) -> float:
        bmi = round((self.weight / (self.height ** 2)), 2)
        return bmi
    
    @computed_field
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 30:
            return  "Normal"
        else:
            return "Obese"
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal["Male", "Female"]], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]




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
def sort_patient(sort_by : Literal['weight', 'bmi', 'height'] = Query(..., description="Sort on the basis of height, weight, or bmi"), order: Literal['asc', 'desc'] = Query(default='asc', description="Choose the order between asc or desc")):

    valid_fields = ["height", "bmi", "weight"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid field, select from {valid_fields}")
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail=f"Invalid order, select from asc or desc")
    

    data = load_data("patients.json")
    sort_order = False if order == 'asc' else True
    sorted_data = sorted(data.values(), key=lambda x : x.get(sort_by, 0), reverse=sort_order)
    return sorted_data


def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f)

@app.post('/create')
def create_patient(patient: Patient):

    # Load existing data
    data = load_data("patients.json")

    # Check if patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")
    
    # Add new patient if not exists
    data[patient.id] = patient.model_dump(exclude=["id"])

    # Save into JSON file
    save_data(data)

    return JSONResponse(status_code=201, content={"message": f"Patient with id {patient.id} has been added successfully."})


@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
    
    data = load_data(file_path="patients.json")

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    existing_patient_info = data[patient_id]
    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    # existing_patient_info --> Pydantic object --> updated bmi + verdict --> Dictionary
    existing_patient_info['id'] = patient_id
    patient_info = Patient(**existing_patient_info)
    existing_patient_info = patient_info.model_dump(exclude='id')

    
    # Add this to the actual data
    data[patient_id] = existing_patient_info

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'Patient successfuly updated'})