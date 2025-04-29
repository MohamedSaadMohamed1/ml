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


app = FastAPI()


# نموذج الإدخال المعدل
class EmployeeInput(BaseModel):
    Risk: str  # 'High Risk', 'Moderate Risk', 'Low Risk'
    Working_Hours: int  # 20, 35, 45, 50
    Recommendation: Optional[str] = None  # أصبح اختياريًا

# نموذج الإخراج
class EmployeeOutput(BaseModel):
    Risk: str
    Working_Hours: int
    Truth: float
    Indeterminacy: float
    Falsity: float
    Refined_Recommendation: str

# قاعدة التوصيات
DEFAULT_RECOMMENDATIONS = {
    "High Risk": "Immediate rest and workload reduction required",
    "Moderate Risk": "Monitor and schedule regular breaks",
    "Low Risk": "Maintain current schedule with optional breaks"
}

def compute_neutrosophic_values(risk: str, working_hours: int):
    risk_truth = {'High Risk': 1.0, 'Moderate Risk': 0.7, 'Low Risk': 0.3}
    working_hours_indeterminacy = {20: 0.2, 35: 0.5, 45: 0.7, 50: 0.9}
    
    T = risk_truth[risk]
    I = working_hours_indeterminacy[working_hours]
    F = max(0, 1 - T - I)
    
    return T, I, F

def refined_recommendation(T: float, I: float, F: float, risk: str, custom_recommendation: Optional[str] = None):
    base_recommendation = custom_recommendation if custom_recommendation else DEFAULT_RECOMMENDATIONS[risk]
    
    if T > 0.7 and F < 0.3:
        return f"URGENT: {base_recommendation}"
    elif I > 0.6:
        return f"CLARIFY: {base_recommendation} (High workload uncertainty)"
    else:
        return f"NORMAL: {base_recommendation}"

@app.post("/process-employee/", response_model=EmployeeOutput)
async def process_employee(employee: EmployeeInput):
    T, I, F = compute_neutrosophic_values(employee.Risk, employee.Working_Hours)
    refined_rec = refined_recommendation(
        T, I, F, 
        employee.Risk,
        employee.Recommendation
    )
    
    return {
        "Risk": employee.Risk,
        "Working_Hours": employee.Working_Hours,
        "Truth": T,
        "Indeterminacy": I,
        "Falsity": F,
        "Refined_Recommendation": refined_rec
    }

# ------------------ API Endpoints ------------------
@app.post("/predict")
async def predict(request: TextRequest):
    return predict_text(request.text)
