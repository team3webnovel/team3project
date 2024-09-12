from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    # 회원가입 SQL 문 작성
    insert_query = f"""
        INSERT INTO users (id, username, email, password) 
        VALUES (user_seq.NEXTVAL, :username, :email, :password)
    """

    try:
        # 회원가입 처리
        execute_query(insert_query, {"username": username, "email": email, "password": password})
        message = "회원가입이 성공적으로 완료되었습니다!"
    except Exception as e:
        message = f"회원가입 중 오류가 발생했습니다: {str(e)}"

    return templates.TemplateResponse("register.html", {"request": request, "message": message})
