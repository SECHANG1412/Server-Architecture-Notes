from fastapi import FastAPI, Depends, HTTPException, status
from typing import Optional

app = FastAPI()

########################################
# --- 의존성 함수(Dependable) 정의 ---
########################################

# 1. 공통 쿼리 파라미터 처리를 위한 의존성 함수
async def common_parameters(
        q: Optional[str] = None,    # 검색 쿼리 (선택적)
        skip: int = 0,              # 건너뛸 항목 수 (기본값 0)
        limit: int = 100            # 가져올 최대 항목 수 (기본값 100)
):
    
    # 딕셔너리 형태로 파라미터들을 묶어서 반환
    return {
        "q": q,
        "skip": skip,
        "limit": limit
    } 


# 2. 간단한 API 키 확인을 위한 의존성 함수
# 실제로는 더 안전한 방식(예: 헤더 사용, 토큰 검증)을 사용해야 합니다!
async def verify_api_key(x_api_key: Optional[str] = None):
    # 전달받은 x_api_key 값이 "fakeapikey"와 다른지 확인한다.
    if x_api_key != "fakeapikey":
        # API 키가 일치하지 않으면 403 에러를 발생시킨다.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,  # 상태 코드를 403 Forbidden으로 설정한다.
            detail="Invalid API Key"                # 에러 메시지를 "Invalid API Key"로 설정한다.
        )
    # API 키가 유효하면 x_api_key 값을 그대로 반환한다.
    return x_api_key


# 3. 하위 의존성 예시: verify_api_key 의존성을 사용하는 또 다른 의존성
async def verify_admin_access(
        # verify_api_key의 결과를 api_key 변수에 주입받는다.
        api_key: str = Depends(verify_api_key)
):
    # 관리자 접근이 확인되었음을 콘솔에 출력한다.
    print(f"관리자 접근 확인됨 (API 키: {api_key})")

    # 관리자임을 나타내는 정보를 딕셔너리로 반환한다.
    return {
        "is_admin": True
    }


#################################################
# --- API 엔드포인트 정의 (의존성 주입 사용) ---
#################################################

@app.get("/items/")
async def read_items(
    commons: dict = Depends(common_parameters)  # common_parameters의 반환값을 commons 변수에 주입받는다.
):
    print(f"요청 파라미터: {commons}") 

    # 아이템 데이터를 리스트 형태로 생성한다. 
    items_data = [
        {"item_name": "Item 1"},    # 첫 번째 아이템 정보를 담은 딕셔너리이다.
        {"item name": "ITem 2"}     # 두 번째 아이템 정보를 담은 딕셔너리이다.
    ]

    # 메시지, 파라미터, 데이터를 포함한 딕셔너리를 반환한다.
    return {
        "message": "Reading items",
        "params": commons,
        "data": items_data
    }

@app.get("/users/")
async def read_users(
    commons: dict = Depends(common_parameters)
):
    print(f"요청 파라미터: {commons}")
    users_data = [
        {"user_name": "User 1"},
        {"user_name": "User 2"}
    ]
    return {
        "message": "Reading users",
        "params": commons,
        "data": users_data
    }

@app.get("/secure-data/")
async def read_secure_data(
    api_key: str = Depends(verify_api_key)
):
    print(f"보안 데이터 접근 허용됨 (API 키: {api_key})")
    return {
        "message": "This is secure data!",
        "requester_api_key": api_key
    }

@app.get("/admin-only/")
async def read_admin_data(
    admin_info: dict = Depends(verify_admin_access)
):
    print(f"관리자 데이터 접근 허용됨: {admin_info}")
    return {
        "message": "Welcome, Admin!",
        "access_level": admin_info
    }