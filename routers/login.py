from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from logger import log_function_call

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@log_function_call
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@log_function_call
@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    if email == "test@example.com" and password == "password":
        return {"message": "로그인 성공!"}
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error_message": "잘못된 이메일 또는 비밀번호입니다."})
