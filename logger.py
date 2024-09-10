import logging
from functools import wraps
import time


def log_function_call(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()  # 함수 시작 시간 기록
        logging.info(f"Running function: {func.__name__}")  # 함수 이름 로깅
        logging.debug(f"Arguments: {args}, {kwargs}")  # 함수 인자 로깅

        try:
            result = await func(*args, **kwargs)  # 함수 실행
            elapsed_time = time.time() - start_time  # 실행 시간 계산
            logging.debug(f"Return value: {result}")  # 함수 반환값 로깅
            logging.info(f"Finished {func.__name__} in {elapsed_time:.4f} seconds")  # 완료 시간 로깅

            # 결과가 dict(예: JSON 응답)일 경우, 그 내용을 추가 로깅
            if isinstance(result, dict):
                logging.info(f"Response data: {result}")

            return result
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")  # 에러 발생 시 로깅
            raise e

    return async_wrapper
