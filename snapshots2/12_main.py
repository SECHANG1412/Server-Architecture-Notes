from fastapi import FastAPI, status, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


# --- 가상 데이터베이스 ---
items_db = {
    1: {"name": "Laptop", "price": 1200.0},
    2: {"name": "Keyboard", "price": 75.0}
}

item_next_id = 3


# --- Pydantic 모델 ---
class Item(BaseModel):
    name: str
    price: float



# --- API 엔드포인트 정의 ---

# 1. 기본 성공 상태 코드 설정 (POST -> 201 Created)
@app.post("/items/", status_code=status.HTTP_201_CREATED, response_model=Item)
async def create_item(item: Item):

    # 전역 변수 item_next_id를 이 함수 안에서 수정하겠다고 표시한다.
    global item_next_id

    # items_db에 item_next_id 번호로 들어온 item 내용을 딕셔너리로 바꿔 저장한다.
    items_db[item_next_id] = item.model_dump()

    # 새로 만든 아이템의 id와 item 내용을 합쳐서 create_item_info에 저장한다.
    create_item_info = {"id": item_next_id, **item.model_dump()}
    item_next_id += 1
    print(f"아이템 생성됨: {create_item_info}")

    # 성공 시 자동으로 201 상태 코드와 함께 생성된 아이템 정보 반환 (response_model 적용됨)
    # 실제로는 DB에서 생성된 객체를 반환하는 것이 좋음
    return create_item_info



# 2. 기본 성공 상태 코드 설정 (DELETE -> 204 No Content)
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):

    # item_id가 items_db 안에 있는지 확인한다.
    if item_id in items_db:
        print(f"아이템 삭제됨: ID={item_id}")

        # items_db에서 해당 item_id 데이터를 삭제한다.
        del items_db[item_id] 

        # 204 상태 코드는 본문(body)을 포함하지 않아야 함
        # FastAPI는 status_code=204이고 반환값이 None이면 자동으로 빈 본문을 보냄
        return None
    else:
        # 아이템 없으면 404 오류 발생 (HTTPException은 status_code 매개변수보다 우선함)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    


# 3. 함수 내 로직에 따라 상태 코드 동적 변경 (Response 객체 직접 반환)
@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item):
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Item not found"
        )
    
    # 현재 저장된 데이터와 새로 받은 데이터가 같은지 확인한다.
    if items_db[item_id] == item.model_dump():
        # 변경 사항 없음 -> 304 Not Modified 반환
        # Reponse 객체를 직접 반환하면 response_model은 무시됨
        print(f"아이템 변경 없음: ID={item_id}")
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    
    # 현재 저장된 데이터와 새로 받은 데이터가 다를 때 처리한다.
    else:
        # items_db에서 해당 item_id 데이터를 새로 받은 데이터로 바꿔 저장한다.
        items_db[item_id] = item.model_dump()
        print(f"아이템 업데이트됨: ID={item_id}, Data={items_db[item_id]}")
        # 여기서는 Pydantic 모델 객체를 반환하여 FastAPI의 자동 처리 + response_model 활용
        return items_db[item_id]
    


# 4. Response 객체 직접 반환 시 주의점 예시
@app.get("/legacy-data", response_model=Item)
async def get_legacy_data():

    # XML 모양의 문자열 데이터를 legacy_content에 저장한다.
    legacy_content = "<legacy><name>Old Data</name><price>10.0</price></legacy>"

    # legacy_content를 본문으로 하고,
    # 미디어 타입을 application/xml로 하고,
    # 상태 코드를 200으로 하는 응답을 만들어 반환한다.
    return Response(
        content=legacy_content,
        media_type="application/xml",
        status_code=200
    )