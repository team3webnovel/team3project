from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import generate_music, generate_image, login, register  # 추가된 라우터들
from logger import log_function_call
import logging

# 기본 로깅 설정
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
logger.debug("FastAPI 애플리케이션이 실행되었습니다.")
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

# 라우터 등록
app.include_router(generate_music.router)
app.include_router(generate_image.router)
app.include_router(login.router)
app.include_router(register.router)

@log_function_call
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
