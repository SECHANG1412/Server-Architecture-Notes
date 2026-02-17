from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


# --- Pydantic 모델 정의 (고급 유효성 검사 추가) ---

class Item(BaseModel):
    # Field를 사용하여 추가 제약 조건 설정
    name: str = Field(
        min_length=3,
        max_length=50,
        title="Item Name",
        description="The name of the item(3 to 50 characters).",
        examples=["Gaming Keyboard"]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=300,
        title="Item Description",
        description="Optional decription of the item (max 300 characters)."
    )
    price: float = Field(
        gt=0,
        le=100000.0,
        title="Price",
        description="The price of the item (must be positive and <= 100,000)."
    )
    tax: Optional[float] = Field(
        default=None,
        gt=0,
        title="tax",
        description="Optional tax amount (must be positive)."
    )
    tags: List[str] = Field(
        default=[],
        min_length=1,
        max_length=5,
        title="Tags",
        description="List of tags for the item (1 to 5 tags)."
    )

    # --- 커스텀 유효성 검사기 ---
    # @field_validator를 사용하여 특정 필드에 대한 커스텀 검증 로직 추가 (Pydantic V2 방식)
    # 클래스 메서드로 정의해야 합니다.
    @field_validator('name')
    @classmethod
    def name_must_not_be_admin(cls, v: str):
    # 'v'는 검증할 필드의 값입니다.

        if "admin" in v.lower():
            raise ValueError("Item name cannot contain 'admin'")
            # 유효성 검사 실패 시 valueError 발생
        
        return v.title()
        # 유효성 검사 통과 시 값을 그대로 또는 수정하여 반환
        # 이름을 Title Case로 변환하여 반환



app = FastAPI()


# 임시 데이터 저장소 (간단한 딕셔너리 사용)
items_db = {}


# --- API 엔드포인트 정의 ---

# "/items/" 경로로 POST 요청이 오면 아래 함수를 실행하고, 성공하면 상태 코드를 201로 준다.
@app.post("/items/", status_code=201)
async def create_item(item: Item):
    item_id = len(items_db) + 1             # items_db에 들어있는 아이템 개수에 1을 더해서 새 item_id를 만든다.
    items_db[item_id] = item.model_dump()   # item을 딕셔너리로 바꿔서 items_db에 item_id 키로 저장한다.

    return {
        "item_id": item_id,    
        **items_db[item_id]     
    }

# "/items/{item_id}" 경로로 GET 요청이 오면 아래 함수를 실행한다.
@app.get("/items/{item_id}")
async def read_item(item_id: int):
# URL 경로에서 item_id를 정수로 받아서 read_item 함수를 실행한다.

    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
        # 아이템이 없으면 404 Not Found 오류 발생

    return {
        "item_id": item_id,
        **items_db[item_id]
    }