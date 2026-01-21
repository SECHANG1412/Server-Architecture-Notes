import time, asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# --- CORS 미들웨어 설정 ---
# 웹 브라우저에서 실행되는 프론트엔드 Javascript 코드로부터의 요청을 허용하기 위함
# 브라우저는 기본적으로 "동일 출처 정책(SOP)"을 적용하므로
# 다른 출처(origin)에서 오는 요청은 서버가 명시적으로 허용해야 함


# 허용할 출처(origin) 목록 - 실제 환경에서는 "*" 대신 구체적인 도메인 명시 권장
origins = [
    "<http://localhost>",                   # 예: 로컬 개발 환경
    "<http://localhost>",                   # 예: React 개발 서버 포트
    "<http://localhost>",                   # 예: Vue 개발 서버 포트
    "<https://your-frontend-domain.com>",   # 실제 서비스 도메인 추가
]


# app.add_middleware를 사용하여 미들웨어 추가
# CORSMiddleware는 FastAPI 내부적으로 가장 바깥 레이어에서 동작
# 실제 엔드포인트 함수보다 항상 먼저 실행됨
app.add_middleware(
    CORSMiddleware,             
    allow_origins=origins,      # origins 목록에 있는 출처의 요청만 허용
    allow_credentials=True,     # 요청 시 쿠키/인증 정보 포함 허용 여부
    allow_methods=["*"],        # 허용할 HTTP 메서드 (GET, POST, PUT 등 모두 허용)
    allow_headers=["*"],        # 허용할 HTTP 요청 헤더 (모든 헤더 허용)
)




# --- 커스텀 미들웨어 정의 ---
# 모든 HTTP 요청에 대해 처리 시간을 측정하고 응답 헤더에 추가하는 미들웨어


# HTTP 요청/응답 사이클에 적용될 미들웨어임을 명시
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):

    # 1. 요청 처리 전 로직 (선택 사항)
    # 클라이언트 요청이 엔드포인트에 도달하기 "직전" 시점
    start_time = time.time()
    print(f"Request received: {request.method} {request.url.path}")

    # 2. 다음 미들웨어 또는 경로 작동 함수 호출 (필수!)
    # call_next 함수는 
    #   - 다음 미들웨어가 있으면 그 미들웨어를 호출하고
    #   - 없으면 실제 엔드포인트 함수(read_root, ping 등)를 호출
    #
    # 반드시 await 해야 하며,
    # await 하지 않으면 요청이 멈추고 응답도 반환되지 않는다
    response = await call_next(request)

    # 3. 응답 처리 후 로직 (선택 사항)
    # 엔드포인트 함수 실행이 끝나고,
    # 응답이 클라이언트로 나가기 직전 시점
    process_time = time.time() - start_time

    # 응답 헤더에 'X-Process-Time'이라는 커스텀 헤더 추가
    # 모든 API 응답에 공통으로 포함됨
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    print(f"Response sent. Process time: {process_time:.4f} sec")

    return response




# --- 간단한 API 엔드포인트 정의 ---

# 미들웨어가 이 함수 실행 전후로 작동합니다. 
# CORS 설정에 따라 다른 출처의 프론트엔드에서 호출 가능합니다.
@app.get("/")
async def read_root():
    # 이 함수는 미들웨어 내부의 call_next()에 의해 호출됨
    return {"message": "Hello World with Middleware and CORS!"}


# 간단한 health check 또는 테스트용 엔드포인트
# 역시 미들웨어와 CORS의 영향을 받습니다.
# 잠시 지연을 주어 처리 시간 헤더 확인 (예시)
@app.get("/ping")
async def ping():
    # asyncio.sleep은 이벤트 루프를 블로킹하지 않는 비동기 대기
    await asyncio.sleep(0.1)  
    return {"message": "pong"}