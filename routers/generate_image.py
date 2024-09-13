from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
import os
import logging
import base64

from logger import log_function_call

router = APIRouter()

# 템플릿 경로 설정
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

# 환경 변수에서 Base64로 인코딩된 API 키를 가져옴
encoded_api_key = os.getenv("ENCODED_API_KEY", "NmYzNjE3ZjYtOTUwYi00MDlmLThhODMtZjhmNGYwYzY2ZmIx")

# Base64로 인코딩된 API 키를 디코딩하여 API 키로 사용
LEONARDO_API_KEY = base64.b64decode(encoded_api_key).decode('utf-8')


@log_function_call
@router.post("/generate-image", response_class=HTMLResponse)
async def generate_image(request: Request, prompt: str = Form(...)):
    """POST 요청을 통해 이미지 생성을 요청하는 엔드포인트"""
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    post_headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    # payload 정의
    payload = {
        "alchemy": True,
        "contrastRatio": 0,
        "prompt": prompt,  # 사용자로부터 받은 프롬프트 사용
        "num_images": 4,
        "width": 1024,
        "height": 768,
        "guidance_scale": 7,
        "modelId": "b24e16ff-06e3-43eb-8d33-4416c2d75876",
        "presetStyle": "DYNAMIC",
        "scheduler": "KLMS",
        "sd_version": "v1_5",
        "tiling": True,
    }

    try:
        # POST 요청으로 이미지 생성 시작
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=post_headers)
            if response.status_code == 200:
                data = response.json()
                generation_id = data["sdGenerationJob"]["generationId"]  # 생성된 작업의 ID
                logging.info(f"Image generation started with ID: {generation_id}")

                # POST 요청 성공 시 상태 확인을 위한 GET 요청으로 리다이렉트
                return RedirectResponse(f"/check-status/{generation_id}", status_code=303)
            else:
                logging.error(f"Image generation failed: {response.text}")
                return templates.TemplateResponse("generate_image.html", {
                    "request": request,
                    "error_message": "이미지 생성에 실패했습니다."
                })

    except Exception as e:
        logging.error(f"Error generating image: {str(e)}")
        return templates.TemplateResponse("generate_image.html", {
            "request": request,
            "error_message": "이미지 생성 중 오류가 발생했습니다."
        })


@log_function_call
@router.get("/check-status/{generation_id}", response_class=HTMLResponse)
async def check_status(request: Request, generation_id: str):
    """GET 요청을 통해 이미지 생성 상태를 확인하는 엔드포인트"""
    url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
    headers = {
        "Authorization": f"Bearer {LEONARDO_API_KEY}",
        "Accept": "application/json",
    }

    try:
        # GET 요청으로 이미지 생성 상태 확인
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # 생성된 이미지의 URL 추출
                image_urls = [image['url'] for image in data['generations_by_pk']['generated_images'] if
                              not image['nsfw']]

                return templates.TemplateResponse("generate_image.html", {
                    "request": request,
                    "image_urls": image_urls
                })
            else:
                logging.error(f"Failed to fetch image status: {response.text}")
                return templates.TemplateResponse("generate_image.html", {
                    "request": request,
                    "error_message": "이미지 상태를 가져오는 중 오류가 발생했습니다."
                })

    except Exception as e:
        logging.error(f"Error fetching image status: {str(e)}")
        return templates.TemplateResponse("generate_image.html", {
            "request": request,
            "error_message": "이미지를 가져오는 중 오류가 발생했습니다."
        })
