
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List
from encryption import encrypt, decrypt
from schemas import Note, NoteIn, TextRequest
from auth import authenticate_user, create_access_token, get_current_user, users_db
from service import predict_text

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/predict")
def predict(request: TextRequest):
    return predict_text(request.text)
