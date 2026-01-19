from fastapi import FastAPI


# FastAPI 애플리케이션 객체 생성
app = FastAPI()


# 루트 경로(/)를 처리하는 비동기 함수
async def read_root():
    # JSON 응답으로 변환될 데이터 반환
    return {"message":"Hello World"}