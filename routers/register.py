from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error_message": "비밀번호가 일치하지 않습니다."})

    # 회원가입 처리 로직 추가 (DB 저장, 이메일 중복 확인 등)
    return templates.TemplateResponse("register.html", {"request": request, "success_message": "회원가입이 완료되었습니다."})
