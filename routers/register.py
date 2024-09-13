import logging
import hashlib  # hashlib 라이브러리 추가
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from db.connection import open_db_connection  # DB 연결 함수

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


# 회원가입 폼을 제공하는 GET 엔드포인트
@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    """회원가입 폼을 제공하는 GET 엔드포인트"""
    return templates.TemplateResponse("register.html", {"request": request})


# 회원가입 POST 요청을 처리하는 엔드포인트
@router.post("/register", response_class=HTMLResponse)
async def register(
        request: Request,
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
):
    """간단한 회원가입 처리"""

    # SHA-256 해시 생성
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    connection = open_db_connection()  # DB 연결
    if connection:
        cursor = connection.cursor()
        try:
            # 사용자 정보를 users 테이블에 삽입하는 SQL문
            # 해시화된 비밀번호를 저장
            cursor.execute("""
                INSERT INTO users (username, email, password) 
                VALUES (:username, :email, :password)
            """, {"username": username, "email": email, "password": hashed_password})

            connection.commit()  # 커밋하여 변경사항 적용

            return RedirectResponse(url="/login", status_code=303)

            # 성공 메시지를 사용자에게 전달
            return templates.TemplateResponse("register.html", {
                "request": request, "message": "회원가입이 성공적으로 완료되었습니다!", "status": "success"
            })

        except Exception as e:
            logging.error(f"사용자 등록 중 오류 발생: {e}")
            return templates.TemplateResponse("register.html", {
                "request": request, "message": f"회원가입 중 오류가 발생했습니다: {e}", "status": "error"
            })

        finally:
            cursor.close()  # 커서 닫기
            connection.close()  # 연결 닫기

    else:
        logging.error("DB 연결을 열 수 없습니다.")
        return templates.TemplateResponse("register.html", {
            "request": request, "message": "DB 연결 중 문제가 발생했습니다.", "status": "error"
        })
