import subprocess
import os
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from suno_functions import generate_music_from_suno, download_music
from logger import log_function_call

router = APIRouter()

# 템플릿 폴더 경로 설정 (경로를 templates 폴더로 맞춤)
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

# 음악 파일 저장 경로 설정
music_output_dir = os.path.join(os.path.dirname(__file__), "../suno/generated_music")
if not os.path.exists(music_output_dir):
    os.makedirs(music_output_dir)

# suno-api 실행 함수
@log_function_call
def start_suno_api():
    try:
        process = subprocess.Popen(["npm", "start"], cwd="./suno/suno-api", shell=True)
        process.communicate()
        print("suno-api started successfully.")
    except Exception as e:
        print(f"Failed to start suno-api: {str(e)}")


# GET 요청: 음악 생성 폼을 제공
@log_function_call
@router.get("/generate-music", response_class=HTMLResponse)
async def get_generate_music_form(request: Request):
    return templates.TemplateResponse("generate_music.html", {"request": request})


# POST 요청: 사용자가 입력한 프롬프트로 음악 생성
@log_function_call
@router.post("/generate-music", response_class=HTMLResponse)
async def generate_music(request: Request,
                         prompt: str = Form(...),
                         make_instrumental: bool = Form(False)):
    try:
        # suno-api 시작
        start_suno_api()

        # 비동기 함수 호출 시 await 사용
        music_data = await generate_music_from_suno(prompt, make_instrumental)

        if music_data and isinstance(music_data, list) and len(music_data) > 0:
            for idx, music_info in enumerate(music_data):
                audio_url = music_info.get("audio_url")
                if audio_url:
                    file_path = os.path.join(music_output_dir, f"music_{idx + 1}.mp3")
                    await download_music(audio_url, file_path)  # 비동기 다운로드 함수 호출
                    print(f"Music saved at: {file_path}")

            return templates.TemplateResponse("result.html", {
                "request": request,
                "music_list": music_data
            })

        return templates.TemplateResponse("generate_music.html", {
            "request": request,
            "error_message": "음악 파일 생성에 실패했습니다."
        })

    except Exception as e:
        # 발생한 예외를 로그에 남기고 템플릿에 전달
        print(f"Error occurred: {str(e)}")
        return templates.TemplateResponse("generate_music.html", {
            "request": request,
            "error_message": f"음악 파일 생성에 실패했습니다. 에러: {str(e)}"
        })
