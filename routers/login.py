import logging
import hashlib  # hashlib 추가
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from db.connection import open_db_connection  # DB 연결 함수

router = APIRouter()
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


# 로그인 폼을 제공하는 GET 엔드포인트
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """로그인 폼을 제공하는 GET 엔드포인트"""
    return templates.TemplateResponse("login.html", {"request": request})


# 로그인 POST 요청을 처리하는 엔드포인트
@router.post("/login", response_class=HTMLResponse)
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
):
    """로그인 처리"""

    # SHA-256 해시 생성 (입력된 비밀번호를 해시화)
    hashed_input_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    connection = open_db_connection()  # DB 연결
    if connection:
        cursor = connection.cursor()
        try:
            # 사용자 정보를 users 테이블에서 조회하는 SQL문
            cursor.execute("""
                SELECT username, password FROM users WHERE username = :username
            """, {"username": username})

            user = cursor.fetchone()  # 조회된 사용자 정보

            if user:
                db_username, db_password = user

                # 입력된 비밀번호의 해시와 DB에 저장된 해시 비교
                if hashed_input_password == db_password:
                    return RedirectResponse(url="/", status_code=303)  # 메인 페이지로 리다이렉트
                else:
                    # 비밀번호가 틀린 경우
                    return templates.TemplateResponse("login.html", {
                        "request": request,
                        "error_message": "잘못된 비밀번호입니다."
                    })
            else:
                # 사용자 정보가 없는 경우
                return templates.TemplateResponse("login.html", {
                    "request": request,
                    "error_message": "존재하지 않는 사용자입니다."
                })

        except Exception as e:
            logging.error(f"로그인 중 오류 발생: {e}")
            return templates.TemplateResponse("login.html", {
                "request": request, "error_message": f"로그인 중 오류가 발생했습니다: {e}"
            })

        finally:
            cursor.close()  # 커서 닫기
            connection.close()  # 연결 닫기

    else:
        logging.error("DB 연결을 열 수 없습니다.")
        return templates.TemplateResponse("login.html", {
            "request": request, "error_message": "DB 연결 중 문제가 발생했습니다."
        })