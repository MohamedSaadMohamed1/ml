
from pydantic import BaseModel

class NoteIn(BaseModel):
    content: str

class Note(NoteIn):
    id: int

class TextRequest(BaseModel):
    text: str
