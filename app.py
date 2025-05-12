from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List
from encryption import encrypt, decrypt
from schemas import Note, NoteIn, TextRequest
from auth import authenticate_user, create_access_token, get_current_user, users_db
from service import predict_text
from pydantic import BaseModel
from typing import Optional
import pandas as pd


# ----- FastAPI App -----
app = FastAPI()

# ----- Input/Output Models -----
class EmployeeInput(BaseModel):
    Risk: str  # 'High Risk', 'Moderate Risk', 'Low Risk'
    Working_Hours: int  # 20, 35, 45, 50

class EmployeeOutput(BaseModel):
    Risk: str
    Working_Hours: int
    Truth: float
    Indeterminacy: float
    Falsity: float
    Refined_Recommendation: str

# ----- Neutrosophic Computation -----
def compute_neutrosophic_values(risk: str, working_hours: int):
    risk_truth = {'High': 1.0, 'Moderate': 0.7, 'Low': 0.3}
    T = risk_truth.get(risk, 0.0)

    # Indeterminacy Calculation
    min_hours = 20
    max_hours = 60
    min_I = 0.1
    max_I = 0.9

    # Clamp and normalize working hours
    clamped_hours = max(min_hours, min(working_hours, max_hours))
    I = min_I + ((clamped_hours - min_hours) / (max_hours - min_hours)) * (max_I - min_I)
    I = round(I, 2)

    F = round(max(0, 1 - T - I), 2)
    T = round(T, 2)

    return T, I, F


# ----- Read Recommendation from Excel -----
def get_recommendation_from_file(risk: str, working_hours: int) -> Optional[str]:
    try:
        df = pd.read_excel("burnout_recommendations_updated.xlsx")
        row = df[(df['risk'] == risk) & (df['working_hours'] == working_hours)]
        if not row.empty:
            return row.iloc[0]['recommendation']
    except Exception as e:
        print("Error reading Excel file:", e)
    return None

# ----- Generate Final Recommendation -----
def refined_recommendation(T: float, I: float, F: float, base: str):
    if T > 0.7 and F < 0.3:
        return f"URGENT: {base}"
    elif I > 0.6:
        return f"CLARIFY: {base} (High workload uncertainty)"
    else:
        return f"NORMAL: {base}"

# ----- Main Endpoint -----
@app.post("/process-employee/", response_model=EmployeeOutput)
async def process_employee(employee: EmployeeInput):
    T, I, F = compute_neutrosophic_values(employee.Risk, employee.Working_Hours)
    file_recommendation = get_recommendation_from_file(employee.Risk, employee.Working_Hours)

    if not file_recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found for given input.")

    refined = refined_recommendation(T, I, F, file_recommendation)

    return EmployeeOutput(
        Risk=employee.Risk,
        Working_Hours=employee.Working_Hours,
        Truth=T,
        Indeterminacy=I,
        Falsity=F,
        Refined_Recommendation=refined
    )

# ------------------ API Endpoints ------------------
@app.post("/predict")
async def predict(request: TextRequest):
    return predict_text(request.text)
