from fastapi import FastAPI, HTTPException
import email_service
import extract_email
from pydantic import BaseModel, EmailStr


class EmailCreds(BaseModel):
    email: EmailStr
    password: str

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Email API"}


@app.post("/load-emails")
async def load_emails(creds: EmailCreds):
    success = email_service.load_emails_from_inbox(creds.email, creds.password)
    if success:
        return {'message': 'Emails loaded.'}
    else:
        raise HTTPException(status_code=500, detail='Failed to load emails from inbox')



@app.get("/emails/{email_id}")
async def get_email(email_id: int):
    email = extract_email.get_email(email_id)

    if email is None:
        raise HTTPException(status_code=404, detail="Email not found")
    else:
        return email
