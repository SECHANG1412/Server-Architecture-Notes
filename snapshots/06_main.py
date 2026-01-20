from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List

######################################################
# --- Pydantic 모델 정의 (고급 유효성 검사 추가) ---
######################################################

class Item(BaseModel):
    # Field를 사용하여 추가 제약 조건 설정
    # Field는 단순한 기본값 설정용이 아니라 "검증 규칙 + OpenAPI 문서 메타데이터"를 동시에 정의하는 도구
    name: str = Field(
        min_length=3,                                               # 최소 길이 3
        max_length=50,                                              # 최대 길이 50
        title="Item Name",                                          # 문서화를 위한 제목 (Swagger 문서에 표시될 필드 제목)
        description="The name of the item (3 to 50 characters).",   # 문서화를 위한 설명 (Swagger 문서 설명)
        examples=["Gaming Keyboard"]                                # 문서화를 위한 예시 (Swagger 문서 예시 값)
    )
    description: Optional[str] = Field(
        default=None,       # 기본값 설정 (요청 본문에서 생략 가능)
        max_length=300,     # 최대 길이 300
        title="Item Description",
        description="Optional description of the item (max 300 characters)."
    )
    price: float = Field(
        gt=0,           # 0보다 커야 함 (greater than)
        le=100000.0,    # 100,000 보다 작거나 같아야 함 (less than or equal)
        title="Price",
        description="The price of the item (must be positive an <= 100,000)."
    )
    tax: Optional[float] = Field(
        default=None,
        gt=0,           # 0보다 커야 함
        title="Tax",
        description="Optional tax amount (must be positive)."
    )
    tags: List[str] = Field(
        default=[],     # 기본값 빈 리스트
        min_length=1,   # 최소 1개의 태그 필요
        max_length=5,   # 최대 5개의 태그 가능
        title="Tags",
        description="List of tags for the item (1 to 5 tags)."
    )

    ######################################################
    # --- 커스텀 유효성 검사기 ---
    ######################################################
    # @field_validator를 사용하여 특정 필드에 대한 커스텀 검증 로직 추가 (Pydantic V2 방식)
    # @field_validator는 Field의 기본 제약(gt, min_length 등) 이후에 실행됨
    # 즉, 기본 검증 통과 → 커스텀 검증 순서
    # 클래스 메서드로 정의해야 합니다.
    @field_validator('name')
    @classmethod
    def name_must_not_be_admin(cls, v: str):    
        # 'v'는 검증할 필드의 값입니다.
        # 'v'는 이미 "str 타입 + 길이 조건"을 통과한 값
        # 여기서는 비즈니스 로직 성격의 검증 수행
        if "admin" in v.lower():
            raise ValueError("Item name cannot contain 'admin'")    # 유효성 검사 실패 시 ValueError 발생
        return v.title()
        # 유효성 검사 통과 시 값을 그대로 또는 수정하여 반환
        # 이름을 Title Case로 변환하여 반환



######################################################
# --- FastAPI 애플리케이션 인스턴스 생성 ---
######################################################
app = FastAPI()


# 임시 데이터 저장소 (간단한 딕셔너리 사용)
# 실제 서비스에서는 DB로 대체됨
items_db = {}


######################################################
# --- API 엔드포인트 정의 ---
######################################################

# 성공 시 201 Created 상태 코드 반환
@app.post("/items/", status_code=201)
async def create_item(item: Item):
    # Pydantic 모델을 통과했다는 것은:
    # 1) 타입 검증
    # 2) Field 제약 조건
    # 3) 커스텀 validator
    # 전부 통과했다는 의미
    item_id = len(items_db) + 1
    items_db[item_id] = item.model_dump()   # Pydantic 모델을 dict로 변환하여 저장

    print(f"아이템 생성 완료: ID={item_id}, Data={items_db[item_id]}")
    
    return {"item_id": item_id, **items_db[item_id]}    # FastAPI는 반환 dict를 자동으로 JSON Response로 직렬화


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    # item_id는 경로 매개변수
    # 타입 변환(int) 실패 시 FastAPI가 자동으로 422 반환

    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
        # 아이템이 없으면 404 Not Found 오류 발생

    # 정상 조회 시 저장된 데이터 반환
    return {"item_id": item_id, **items_db[item_id]}