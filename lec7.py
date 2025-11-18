# Serving ML model with FASTApi

from typing import Literal, Annotated
from pydantic import BaseModel, computed_field, Field
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import pickle           

app = FastAPI()


with open('model.pkl', 'rb') as file:
    model = pickle.load(file)



tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]


class userInput(BaseModel):
    age: Annotated[int, Field(..., description="Age of the user", gt=0, lt=120)]
    weight: Annotated[float, Field(..., description="Weight of the user in kgs", gt=0)]
    height: Annotated[float, Field(..., description="Height of the user in metres", gt=0)]
    income_lpa: Annotated[float, Field(..., description="Annual Income of the user", gt=0)]
    smoker: Annotated[bool, Field(..., description="Is user a smoker")]
    city: Annotated[str, Field(..., description="The city that the user belongs to")]
    occupation: Annotated[Literal['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job'], Field(..., description="Occupation of the user")]

    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight // (self.height ** 2)

    @computed_field
    @property 
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi > 27:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"
    


@app.post('/predict')
def predict_premium(data: userInput):
    input_df = pd.DataFrame([{
    "bmi": data.bmi,
    "age_group": data.age_group,
    "lifestyle_risk": data.lifestyle_risk,
    "city_tier": data.city_tier,
    "income_lpa": data.income_lpa,
    "occupation": data.occupation
}])

    prediction = model.predict(input_df)[0]
    return JSONResponse(status_code=200, content={'predicted_category': prediction})