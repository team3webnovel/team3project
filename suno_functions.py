import httpx  # 비동기 HTTP 클라이언트로 변경
from logger import log_function_call

# Suno API 서버 URL
base_url = 'http://localhost:3000'

# Suno API 호출 함수 (프롬프트와 기악곡 여부 전달)
@log_function_call
async def generate_music_from_suno(prompt, make_instrumental=False):
    try:
        url = f"{base_url}/api/generate"  # /api/generate 엔드포인트 사용
        payload = {
            "prompt": prompt,
            "make_instrumental": make_instrumental,
            "wait_audio": True  # 음악이 생성될 때까지 기다림
        }

        # Suno API로 비동기 요청 보내기
        async with httpx.AsyncClient(timeout=300) as client:  # 타임아웃을 300초(5분)로 설정
            response = await client.post(url, json=payload)

        # 응답 상태 코드와 응답 내용 출력
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")

        # 성공 시 응답 JSON 반환
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return {}

    except httpx.RequestError as e:
        print(f"Request error calling Suno API: {e}")
        return {}
    except Exception as e:
        print(f"Error calling Suno API: {e}")
        return {}

# 음악 파일 다운로드 함수
@log_function_call
async def download_music(audio_url, output_path):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url, stream=True)

        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                async for chunk in response.aiter_bytes(1024):
                    f.write(chunk)
            print(f"Downloaded music to {output_path}")
        else:
            print(f"Failed to download music from {audio_url}")
    except httpx.RequestError as e:
        print(f"Request error downloading music: {e}")
    except Exception as e:
        print(f"Error downloading music: {e}")
