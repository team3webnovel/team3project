from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import httpx
import os
import logging
import base64

from logger import log_function_call

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

# Base64로 인코딩된 API 키 (파워셸에서 인코딩한 값으로 대체하세요)
encoded_api_key = "NmYzNjE3ZjYtOTUwYi00MDlmLThhODMtZjhmNGYwYzY2ZmIx"

# Base64로 인코딩된 값을 디코딩하여 API 키로 사용
LEONARDO_API_KEY = base64.b64decode(encoded_api_key).decode('utf-8')


@log_function_call
@router.get("/generate-image", response_class=HTMLResponse)
async def get_generate_image_form(request: Request):
    """이미지 생성 폼을 렌더링하는 GET 엔드포인트"""
    return templates.TemplateResponse("generate_image.html", {"request": request})


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
    payload = {
        "prompt": prompt,
        "num_inference_steps": 30,
        "width": 1024,
        "height": 768,
        "modelId": "b24e16ff-06e3-43eb-8d33-4416c2d75876",
        "num_images": 1,
        "presetStyle": "DYNAMIC",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=post_headers)
            if response.status_code == 200:
                data = response.json()
                generation_id = data["sdGenerationJob"]["generationId"]
                # POST가 성공하면 GET 요청으로 리다이렉트하여 상태 확인
                return RedirectResponse(f"/check-status/{generation_id}", status_code=303)
            else:
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
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                images_data = response.json()
                # nsfw가 False인 이미지만 필터링
                image_urls = [image['url'] for image in images_data['generations_by_pk']['generated_images'] if
                              not image['nsfw']]

                # 이미지가 성공적으로 생성되었을 경우 템플릿에 전달
                return templates.TemplateResponse("generate_image.html", {
                    "request": request,
                    "image_urls": image_urls
                })
            else:
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
