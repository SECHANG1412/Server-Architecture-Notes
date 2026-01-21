from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI()

##################################################
# --- Pydantic 모델 정의 ---
##################################################

# 사용자 생성을 위한 입력 모델 (비밀번호 포함)
class UserIn(BaseModel):
    # 요청 Body(JSON)가 들어올 때,
    # FastAPI는 이 모델을 보고:
    # 1) JSON 파싱, 2) 타입 검증, 3) 필수/옵션 필드 확인, 4) 실패 시 자동으로 422 응답 생성
    #
    # 이 단계는 "엔드포인트 함수 실행 이전"에 수행됨
    # → 즉, 여기서 검증에 실패하면 create_user 함수 자체가 호출되지 않음
    username: str
    password: str       # 입력 시에는 비밀번호가 필요
    email: EmailStr     # Pydantic의 EmailStr 타입으로 이메일 형식 검증
    full_name: Optional[str] = None


# 사용자 정보를 외부에 보여주기 위한 출력 모델 (비밀번호 제외)
class UserOut(BaseModel):
    # response_model로 사용됨
    # → "이 API는 이 필드만 응답으로 내보낸다"는 계약
    #
    # 이 모델은 "입력 검증"에는 전혀 사용되지 않음
    # → 오직 "응답 직렬화 + 필터링" 용도
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    

# 간단한 아이템 모델 (내부 데이터 표현용)    
class ItemInternal(BaseModel):
    # 실제 DB 모델에 가깝다고 가정
    # → 서버 내부에서만 사용
    #
    # 이 모델은 클라이언트와의 계약(API 스펙)이 아님
    # → 내부 로직 편의를 위한 데이터 구조
    name: str
    price: float
    owner_id: int       # 내부적으로만 사용할 소유자 ID
    secret_code: str    # 외부에 노출하고 싶지 않은 비밀 코드


# 아이템 정보를 외부에 보여주기 위한 출력 모델 (내부 정보 제외)
class ItemPublic(BaseModel):
    # 클라이언트에게 노출 가능한 최소 정보만 정의
    #
    # response_model로 사용될 때
    # ItemInternal → ItemPublic 으로 "자동 변환 + 필터링"이 일어남
    name: str
    price: float


# --- 가상의 데이터 베이스 ---
# 실제로는 DB를 사용하겠지만, 여기서는 간단한 dict와 list 사용
fake_users_db = {}
fake_items_db = {
    1: ItemInternal(name="Keyboard", price=75.0, owner_id=1, secret_code="abc"),
    2: ItemInternal(name="Mouse", price=25.5, owner_id=1, secret_code="def"),
    3: ItemInternal(name="Monitor", price=300.0, owner_id=2, secret_code="ghi")
}


##################################################
# --- API 엔드포인트 정의 ---
##################################################

# 1. 기본 JSON 응답 - 딕셔너리 반환
@app.get("/ping")
async def ping():
    # 딕셔너리를 반환하면 자동으로 JSON 응답이 됩니다.
    #
    # 내부적으로는:
    # dict → JSON 직렬화 → JSONResponse 생성 → 클라이언트 전송
    return {"message": "pong"}



# 2. 사용자 생성 - 입력 모델(UserIn)과 응답 모델(UserOut) 사용
@app.post("/users/", response_model=UserOut, status_code=201)
async def create_user(user: UserIn):
    # 입력은 UserIn 모델로 받음
    # user 객체에는 password 필드가 포함되어 있습니다.
    #
    # 이 시점에서는 이미:
    # - JSON 파싱 완료
    # - 타입/형식 검증 완료
    # - UserIn 인스턴스 생성 완료

    print(f"Creating user: {user.username}, Password: {user.password}")

    # 실제로는 비밀번호를 해싱하여 DB에 저장하는 등의 처리가 필요합니다.
    fake_users_db[user.username] = user

    # 함수는 UserIn 모델 객체(비밀번호 포함)를 반환하지만...
    # 'response_model=UserOut' 때문에 비밀번호는 최종 응답에서 자동으로 필터링됩니다.
    #
    # 반환값 → response_model 적용 → JSON 변환 순서
    return user



# 3. 특정 사용자 정보 조회 - 응답 모델(UserOut) 사용
@app.get("/user/{username}", response_model=UserOut)
async def read_user(username: str):
    # username은 Path Parameter
    # → URL에서 문자열로 추출되어 함수 인자로 전달됨

    if username not in fake_users_db:
        # HTTPException은 FastAPI가 인식하는 "의도된 HTTP 에러"
        # → 자동으로 JSON 에러 응답 생성
        raise HTTPException(status_code=404, detail="User not found")
    
    # DB에서 가져온 UserIn 객체 (비밀번호 포함)
    user_in_db = fake_users_db[username]

    # UserIn 객체를 반환해도 response_model=UserOut에 의해 필터링됨
    return user_in_db



# 4. 아이템 목록 조회 - 응답 모델을 리스트 형태로 사용
# List[ItemPublic] : ItemPublic 모델 객체들의 리스트 형태로 응답 스키마 정의
@app.get("/items/", response_model=List[ItemPublic])
async def read_items():
    
    # 실제 DB에서 가져온 ItemInternal 객체들의 리스트라고 가정
    internal_items_list = list(fake_items_db.values())

    # 반환 시 내부 동작:
    # List[ItemInternal]
    # → 각 요소를 ItemPublic 기준으로 변환
    # → 리스트 전체를 JSON 배열로 직렬화
    return internal_items_list



# 5. 특정 아이템 조회 - 응답 모델(ItemPublic) 사용
@app.get("/items/{item_id}", response_model=ItemPublic)
async def read_single_item(item_id: int):
    # item_id는 Path Parameter
    # → URL 문자열 → int 타입 변환 시도
    # → 실패하면 자동으로 422 응답
    
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # DB에서 가져온 ItemInternal 객체 (secret_code 포함)
    internal_item = fake_items_db[item_id]

    # ItemInternal 객체를 반환해도 response_model=ItemPublic에 의해 필터링됨
    return internal_item

