from fastapi import FastAPI, status, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

##############################################
# --- 가상 데이터베이스 ---
##############################################
items_db = {
		1: {"name": "Laptop", "price": 1200.0}, 
		2: {"name": "Keyboard", "price": 75.0}
}

# 다음에 생성될 아이템의 ID 값
# 실제 DB라면 자동 증가(auto increment)를 DB가 해줌
item_next_id = 3




##############################################
# --- Pydantic 모델 ---
##############################################
# Item은 아이템 데이터의 형식을 정의한 모델이다.
# 이 모델을 기준으로 요청 데이터가 검사되고, 응답 데이터가 정리된다.
class Item(BaseModel):
    name: str       # 아이템의 이름을 문자열로 저장
    price: float    # 아이템의 가격을 숫자로 저장



##############################################
# --- API 엔드포인트 정의 ---
##############################################

# 1. 기본 성공 상태 코드 설정 (POST -> 201 Created)
# "/items/" 주소로 POST 요청이 들어오면 실행된다.한
@app.post("/items/", status_code=status.HTTP_201_CREATED, response_model=Item)
# 요청이 성공하면 201 상태 코드로 응답하고, 응답 데이터 형식은 Item으로 제한한다.
async def create_item(item: Item):
    global item_next_id                         # 함수 안에서 전역 변수 item_next_id를 사용하겠다고 선언
    items_db[item_next_id] = item.model_dump()  # 요청으로 받은 아이템 데이터를 딕셔너리로 변환하여 데이터베이스에 저장

    # 생성된 아이템의 ID와 데이터를 하나의 정보로 묶는다.
    created_item_info = {
        "id": item_next_id,
        **item.model_dump()
    }

    # 다음 아이템을 위해 ID 값을 1 증가시킨다.
    item_next_id += 1

    print(f"아이템 생성됨: {created_item_info}")

    # 반환값은 JSON으로 자동 변환됨
    # 생성된 아이템 정보를 응답으로 반환한다.
    # response_model 설정에 따라 id 필드는 응답에서 자동으로 제외된다.
    return created_item_info



# 2. 기본 성공 상태 코드 설정 (DELETE -> 204 No Content)
# "/items/{item_id}" 주소로 DELETE 요청이 들어오면 실행된다.
# status_code=204 → "성공했지만 돌려줄 내용은 없음"
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):

    # 삭제하려는 아이템이 데이터베이스에 존재하는 경우
    if item_id in items_db:

        # 서버 콘솔에 아이템이 삭제되었음을 출력한다.
        print(f"아이템 삭제됨: ID={item_id}")

        # 데이터베이스에서 해당 아이템을 삭제한다.
        del items_db[item_id]

        # 204 상태 코드이므로 응답 본문 없이 응답을 종료한다.
        return None
    

    # 삭제하려는 아이템이 데이터베이스에 존재하지 않는 경우
    else:
        # 아이템을 찾을 수 없다는 의미로 404 오류를 발생시킨다.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Item not found"
        )




# 3. 함수 내 로직에 따라 상태 코드 동적 변경 (Response 객체 직접 반환)
# PUT 요청은 기존 아이템의 데이터를 수정할 때 사용한다.
@app.put("/items/{item_id}", response_model=Item)   # 수정이 성공하면 기본적으로 Item 형식의 응답을 반환한다.
async def update_item(item_id: int, item: Item):

    # 수정하려는 아이템이 데이터베이스에 없는 경우
    if item_id not in items_db:
        # 아이템이 존재하지 않음을 알리는 404 오류를 발생시킨다.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    

    # 기존 아이템 데이터와 요청으로 들어온 데이터가 완전히 같은 경우
    if items_db[item_id] == item.model_dump():
        print(f"아이템 변경 없음: ID={item_id}")                    # 서버 콘솔에 아이템에 변경 사항이 없음을 출력한다.
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)  # 변경된 내용이 없으므로 304 상태 코드로 응답한다.
    
    # 기존 데이터와 요청 데이터가 다른 경우
    else:
        items_db[item_id] = item.model_dump()                              # 아이템 데이터를 새로운 값으로 업데이트한다.
        print(f"아이템 업데이트됨: ID={item_id}, Data={items_db[item_id]}") # 서버 콘솔에 아이템이 수정되었음을 출력한다.
        return items_db[item_id]                                           # 수정된 아이템 데이터를 응답으로 반환한다.
    

# 4. Response 객체 직접 반환 시 주의점 예시  
# "/legacy-data" 주소로 GET 요청이 들어오면 실행된다.
@app.get("/legacy-data", response_model=Item)
async def get_legacy_data():
    # 오래된 시스템에서 전달된 XML 형식의 데이터라고 가정한다.
    legacy_content = "<legacy><name>Old Data</name><price>10.0</price></legacy>"    

    # XML 데이터를 그대로 응답으로 반환하며,
    # 이 경우 response_model 설정은 적용되지 않는다.
    return Response(
        content=legacy_content,
        media_type="application/xml",
        status_code=200
    )