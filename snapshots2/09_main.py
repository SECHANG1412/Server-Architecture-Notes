from fastapi import FastAPI, HTTPException, Request, status, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

app = FastAPI()


# --- 가상 데이터 ---
items_db = {
    1: {"name": "Keyboard"},
    2: {"name": "Mouse"}
}

# --- 커스텀 예외 정의 ---
# 내가 직접 만든 “에러 타입(이름표)”
# 기본 Exception을 상속해서 UnicornException이라는 새 예외 클래스를 만든다.
class UnicornException(Exception):
    # UnicornException이 만들어질 때 name과 message를 받아서 저장하도록 한다.
    def __init__(self, name: str, message: str = "A unicorn related error occurred"):
        self.name = name        # 예외에 들어온 name 값을 self.name에 저장한다.
        self.message = message  # 예외에 들어온 message 값을 self.name에 저장한다.


# --- 커스텀 예외 핸들러 등록 ---
# 특정 예외가 터졌을 때 “어떤 응답을 보낼지”를 정해주는 함수.
# UnicornException이 발생했을 때 실행할 예외 처리 함수를 등록한다.
# 요청 정보 request와 발생한 예외 exc를 받아서 처리하는 비동기 함수를 만든다.
@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    # JSONResponse로 JSON 응답을 만들어서 반환한다.
    return JSONResponse(
        # HTTP 상태 코드를 418로 설정한다.
        status_code=418,

        # 응답 본문에 들어갈 JSON 내용을 딕셔너리로 만든다.
        content={
            "error_type": "Unicorn Error",  # 에러 종류를 "Unicorn Error"라고 적어서 보낸다.
            "failed_item_name": exc.name,   # 실패한 아이템 이름으로 exc.name 값을 넣어서 보낸다.
            "message": exc.message,         # 메시지로 exc.message 값을 넣어서 보낸다.
            "request_url": str(request.url) # 요청이 들어온 URL을 문자열로 바꿔서 보낸다.
        }
    )


# --- 기본 RequestValidationError 핸들러 재정의 ---
# FastAPI가 “요청 데이터 검증 실패”를 처리하는 기본 규칙을 내가 바꿔치기한 것.
# Pydantic 유효성 검사 실패 시 기본 422 응답 대신 커스텀 응답 반환
# RequestValidationError가 발생했을 때 실행할 예외 처리 함수를 등록한다.
# 요청 정보 request와 발생한 예외 exc를 받아서 처리하는 비동기 함수를 만든다.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    error_details = []      # 사람이 읽기 좋은 오류 설명을 담을 리스트를 만든다.

    # exc.errors()에 들어있는 각 오류 정보를 하나씩 꺼내서 반복한다.
    for error in exc.errors():
        field = " -> ".join(map(str, error['loc']))             # 오류 위치 정보 error['loc']를 문자열로 바꾸고 "->"로 이어서 field에 저장한다.
        message = error['msg']                                  # 오류 메시지 error['msg']를 message에 저장한다.
        error_details.append(f"Field '{field}': {message}")     # "Field '...': ..." 형태의 문장을 만들어 error_details 리스트에 추가한다.
    
    # 간단한 텍스트 응답 또는 커스텀 JSON 응답 반환 가능
    # JSONResponse로 JSON 응답을 만들어서 반환한다.
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,    # 422 대신 400 사용 (선택)\
        
        # 응답 본문에 들어갈 JSON 내용을 딕셔너리로 만든다.
        content={
            "message": "Invalid input provided.",   # 전체 메시지로 "Invalid input provided."를 넣어서 보낸다.
            "details": exc.errors()                 # details에 exc.errors() 결과를 그대로 넣어서 보낸다.    
        }
    )



# --- API 엔드포인트 정의 ---

# 1. HTTPException 사용 예제
# "/items/{item_id}" 경로로 GET 요청이 오면 이 함수를 실행하도록 등록한다.
# item_id를 정수로 받아서 아이템 정보를 돌려주는 비동기 함수를 만든다.
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items_db:
        # 아이템 없으면 404 오류 발생시킴
        # HTTPException을 발생시켜서 요청을 오류로 끝낸다.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,              # 상태 코드 지정
            detail=f"Item with ID {item_id} not found.",        # 오류 메시지 지정
            headers={"X-Error-Source": "Read Item Endpoint"}    # 커스텀 헤더 (선택)
        )
    return items_db[item_id]


# 2. 커스텀 예외 발생 예제 - 내가 만든 예외(UnicornException)를 일부러 발생시키는 예시 코드
# "/unicorns/{name}" 경로로 GET 요청이 오면 이 함수를 실행하도록 등록한다.
# name을 문자열로 받아서 유니콘 관련 응답을 돌려주는 비동기 함수를 만든다.
@app.get("/unicorns/{name}")
async def generate_unicorn_error(name: str):
    if name == "sparkle":
        # 특정 조건에서 커스텀 예외 발생
        raise UnicornException(
            name=name,
            message="Sparkle caused a rainbow overload!"
        )
    elif name == "invalid":
        # ValueError 발생 시 기본 500 오류 발생 (핸들러 없으므로)
        # 또는 별도 핸들러 등록 가능
        raise ValueError("This is an unhandled ValueError")

    return {
        "unicorn_name": name,
        "status": "ok"
    }


# 3. 유효성 검사 오류 발생 예제 (RequestValidationError 재정의 테스트용)
# 요청 데이터 검증이 실패했을 때(RequestValidationError) 어떤 응답이 나가는지 확인하려고 만든 예시 코드
# 요청 바디의 입력 데이터를 검증하기 위한 모델 클래스 InputData를 만든다.
class InputData(BaseModel):
    value: int = Field(gt=10)   # value 필드는 정수이고 10보다 커야 한다는 조건을 설정한다.

# "/validate/" 경로로 POST 요청이 오면 이 함수를 실행하도록 등록한다.
# data를 InputData 형태로 받아서 검증 결과를 돌려주는 비동기 함수를 만든다.
@app.post("/validate/")
async def validate_endpoint(data: InputData):

    # 검증이 통과했을 때 아래 딕셔너리를 반환한다.
    # data.value <= 10 인 요청이 오면 RequestValidationError 발생 -> 커스텀 핸들러 실행됨
    return {
        "message": "Data is valid!",
        "received_value": data.value
    }