from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional

app = FastAPI()

###############################
# --- Pydantic 모델 정의 ---
###############################

# 사용자 생성을 위한 입력 모델(비밀번호 포함)이라는 뜻의 클래스(UserIn)를 만든다.
class UserIn(BaseModel):
    username: str
    password: str       # 입력 시에는 비밀번호가 필요
    email: EmailStr     # Pydantic의 EmailStr 타입으로 이메일 형식 검증
    full_name: Optional[str] = None

# 사용자 정보를 밖으로 보여줄 때 쓰는 출력 모델(UserOut)이라는 클래스를 만든다.
class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

# 아이템을 내부에서 다룰 때 쓰는 모델(ItemInternal)이라는 클래스를 만든다.
class ItemInternal(BaseModel):
    name: str
    price: float
    owner_id: int       # 내부적으로만 사용할 소유자 ID
    secret_code: str    # 외부에 노출하고 싶지 않은 비밀 코드

# 아이템을 밖으로 보여줄 때 쓰는 모델(ItemPublic)이라는 클래스를 만든다.
class ItemPublic(BaseModel):
    name: str      
    price: float


###############################
# --- 가상 데이터베이스 ---
###############################
# 실제로는 DB를 사용하겠지만, 여기서는 간단한 dict와 list 사용

# 가짜 사용자 데이터베이스로 쓸 빈 빈셔너리를 만든다.
fake_users_db = {}

# 가짜 아이템 데이터베이스로 쓸 딕셔너리를 만들고, 아이템 3개를 미리 넣는다.
fake_items_db = {
    1: ItemInternal(name="Keyboard", price=75.0, owner_id=1, secret_code="abc"),
    2: ItemInternal(name="Mouse", price=25.5, owner_id=1, secret_code="def"),
    3: ItemInternal(name="Monitor", price=300.0, owner_id=2, secret_code="ghi"),
}


###############################
# --- API 엔드포인트 정의 ---
###############################

# 1. 기본 JSON 응답 - 딕셔너리 반환
# /ping 주소로 GET 요청이 오면 아래 함수를 실행하도록 등록한다.
@app.get("/ping")
async def ping():
    # {"message": "pong"} 딕셔너리를 만들어서 반환한다.
    # 딕셔너리를 반환하면 자동으로 JSON 응답이 됩니다.
    return {
        "message": "pong"
    }



# 2. 사용자 생성 - 입력 모델(UserIn)과 응답 모델(UserOut) 사용
# /users/ 주소로 POST 요청이 오면 아래 함수를 실행하고, 응답은 UserOut 모양으로 보내며, 상태 코드는 201로 보내도록 등록한다.
@app.post("/users/", response_model=UserOut, status_code=201)
async def create_user(user: UserIn):
# 입력은 UserIn 모델로 받음
# user 객체에는 password 필드가 포함되어 있습니다.

    print(f"Creating user: {user.username}, Password: {user.password}")

    # 실제로는 비밀번호를 해싱하여 DB에 저장하는 등의 처리가 필요합니다.
    # fake_users_db 딕셔너리에서 user.username을 키로 사용해서, user 객체 전체를 저장한다.
    fake_users_db[user.username] = user 

    return user



# 3. 특정 사용자 정보 조회 - 응답 모델(UserOut) 사용
# /users/{username} 주소로 GET 요청이 오면 아래 함수를 실행하고, 응답은 UserOut 모양으로 보내도록 등록한다.
@app.get("/users/{username}", response_model=UserOut)
async def read_user(username: str):
    if username not in fake_users_db:
        raise HTTPException (status_code=404, detail="User not found")
    
    # DB에서 가져온 UserIn 객체 (비밀번호 포함)
    # fake_users_db에서 username 키로 저장된 값을 꺼내서 user_in_db 변수에 담는다.
    user_in_db = fake_users_db[username]

    # UserIn 객체를 반환해도 response_model=UserOut에 의해 필터링됨
    return user_in_db



# 4. 아이템 목록 조회 - 응답 모델을 리스트 형태로 사용
# List[ItemPublic] : ItemPublic 모델 객체들의 리스트 형태로 응답 스키마 정의
# /items/ 주소로 GET 요청이 오면 아래 함수를 실행하고, 응답은 ItemPublic 리스트 모양으로 보내도록 등록한다.
@app.get("/items/", response_model=List[ItemPublic])

# 실제 DB에서 가져온 ItemInternal 객체들의 리스트라고 가정
async def read_items():
    # fake_items_db 딕셔너리의 값들만 꺼내서 리스트로 만들고 internal_items_list 변수에 담는다.
    internal_items_list = list(fake_items_db.values())

    # ItemInternal 객체 리스트를 반환하면, 각 객체가 ItemPublic 스키마에 맞춰 필터링됨
    return internal_items_list



# 5. 특정 아이템 조회 - 응답 모델(ItemPublic) 사용
# /items/{item_id} 주소로 GET 요청이 오면 아래 함수를 실행하고, 응답은 ItemPublic 모양으로 보내도록 등록한다.
@app.get("/items/{item_id}", response_model=ItemPublic)
async def read_single_item(item_id: int):
    if item_id not in fake_items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # DB에서 가져온 ItemInternal 객체 (secret_code 포함)
    internal_item = fake_items_db[item_id]

    # ItemInternal 객체를 반환해도 response_model=ItemPublic 에 의해 필터링됨
    return internal_item
