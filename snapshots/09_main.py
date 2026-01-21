from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

app = FastAPI()

# --- 가상 데이터 ---
items_db = {1: {"name": "Keyboard"}, 2: {"name": "Mouse"}}

# --- 커스텀 예외 정의 ---
class UnicornException(Exception):
    # Python 기본 Exception을 상속한 "도메인 전용 예외"
    # HTTP 개념이 전혀 없는 순수 Python 예외
    #
    # 👉 Exception = "문제가 생겼다!" 라고 소리치는 것
    # 👉 UnicornException = "유니콘 때문에 문제가 생겼다!" 라고
    # 👉 우리가 직접 만든 특별한 문제 이름
    def __init__(self, name: str, message: str = "A unicorn related error occurred"):
        self.name = name
        self.message = message
        # 👉 어떤 유니콘 때문에 문제인지 기억해두는 역할


# --- 커스텀 예외 핸들러 등록 ---
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    # UnicornException이 발생하면 이 핸들러가 실행됨
    # 어떤 엔드포인트에서 발생했든 전역(Global)으로 처리됨
    # FastAPI가 이 예외 타입과 핸들러를 자동으로 매핑
    #
    # 👉 쉽게 말하면:
    # 👉 "UnicornException이 나오면,
    # 👉 이 방법으로 대답해줘!" 라고 미리 약속해두는 것
    return JSONResponse(
        status_code=418,
        content={
            "error_type": "Unicorn Error",
            "failed_item_name": exc.name,
            "message": exc.message,
            "request_url": str(request.url)
        }
    )
    # 👉 그냥 에러라고만 말하지 않고
    # 👉 "왜 실패했는지"를 친절하게 알려주는 응답


# --- 기본 RequestValidationError 핸들러 재정의 ---
# Pydantic 유효성 검사 실패 시 기본 422 응답 대신 커스텀 응답 반환
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # exc.errors()로 상세 오류 정보를 얻을 수 있음
    # 이 예외는 엔드포인트 함수 실행 전에 발생
    # 즉, 함수 내부 로직은 아예 실행되지 않음
    #
    # 👉 사용자가 보낸 값이
    # 👉 "규칙에 맞지 않으면" 여기로 바로 옴
    # 👉 아예 함수까지도 안 들어감
    error_details = []
    for error in exc.errors():
        field = " -> ".join(map(str, error['loc'])) # 오류 발생 필드 위치
        message = error['msg']                      # 오류 메시지
        error_details.append(f"Field '{field}': {message}")
        # 👉 어느 부분이 왜 틀렸는지 하나씩 정리

    # 간단한 텍스트 응답 또는 커스텀 JSON 응답 반환 가능
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,    # 422 대신 400 사용 (선택)
        content={
            "message": "Invalid input provided",
            "details": exc.errors()                 # 원본 오류 상세 정보 포함 (선택)
            # "simplified_details": error_details # 단순화된 메시지 포함 (선택)
        }
    )
    # 👉 "너가 보낸 값이 규칙을 어겼어"라고 알려주는 역할



# --- API 엔드포인트 정의 ---

# 1. HTTPException 사용 예제
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    # 이 시점에서는 이미 경로 파라미터 타입 검증(int)이 끝난 상태
    #
    # 👉 item_id는 무조건 숫자
    # 👉 글자를 보내면 여기까지도 못 옴
    if item_id not in items_db:
        # 아이템 없으면 404 오류 발생시킴
        # HTTPException은 FastAPI가 "의도된 HTTP 오류"로 인식
        #
        # 👉 서버가 고장난 게 아니라
        # 👉 "그 물건이 없어!" 라고 알려주는 상황
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,              # 상태 코드 지정
            detail=f"Item with ID {item_id} not found.",        # 오류 메시지 지정
            headers={"X-Error-Source": "Read Item Endpoint"},   # 커스텀 헤더 (선택)
        )
    return items_db[item_id]
    # 👉 있으면 그냥 물건 정보 돌려줌




# 2. 커스텀 예외 발생 예제
@app.get("/unicorns/{name}")
async def generate_unicorn_error(name: str):

    # HTTPException이 아닌 "순수 Python 예외" 발생 예제
    #
    # 👉 일부러 여러 종류의 문제를 만들어보는 연습용
    if name == "sparkle":
        # UnicornException → 커스텀 핸들러가 처리
        #
        # 👉 여기서는 "어떻게 응답할지" 고민 안 함
        # 👉 그냥 문제를 던지고 끝
        raise UnicornException(name=name, message="Sparkle caused a rainbow overload!")
    
    elif name == "invalid":
        # ValueError 발생 시 기본 500 오류 발생 (핸들러 없으므로)
        # 전역 핸들러가 없기 때문에 Internal Server Error
        #
        # 👉 아무도 처리 안 해주면
        # 👉 서버가 "큰 문제 생김!" 이라고 판단
        raise ValueError("This is an unhandled ValueError")
    
    return {"unocorn_name": name, "status": "ok"}




# 3. 유효성 검사 오류 발생 예제 (RequestValidationError 재정의 테스트용)
class InputData(BaseModel):
    # 요청 본문(JSON)을 자동 검증하는 Pydantic 모델
    #
    # 👉 사용자가 보낸 종이에
    # 👉 "이 규칙을 지켜야 해!" 라고 적어놓은 것
    value: int = Field(gt=10)
    # 👉 숫자여야 하고
    # 👉 10보다 커야 함



@app.post("/validate/")
async def validate_endpoint(data: InputData):
    # data.value <= 10 인 요청이 오면
    # 엔드포인트 실행 전에 RequestValidationError 발생
    # 위에서 재정의한 핸들러가 실행됨
    #
    # 👉 규칙을 지킨 경우에만
    # 👉 여기 코드가 실행됨
    return {"message": "Data is valid!", "received_value": data.value}