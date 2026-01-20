from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional


######################################################
# --- Pydantic 모델 정의 ---
######################################################

# BaseModel을 상속받아 데이터 모델 클래스를 만듭니다.
# 이 클래스는 요청 본문의 데이터 구조(스키마)를 정의합니다.
class Item(BaseModel):
    # FastAPI는 이 타입 힌트를 기준으로
    # 요청 JSON의 필드 존재 여부 + 타입을 자동 검증합니다.
    name: str                           # 필수 필드, 문자열 타입이어야 함
    description: Optional[str] = None   # 선택적 필드(기본값 None), 문자열 또는 None 이어야 함
    price: float                        # 필수 필드, 실수 타입이어야 함
    tax: Optional[float] = None         # 선택적 필드(기본값 None), 실수 또는 None 이어야 함



######################################################
# --- FastAPI 애플리케이션 인스턴스 생성 ---
######################################################

# FastAPI 객체는 전체 웹 애플리케이션의 시작점
# 라우터, 미들웨어, 이벤트 핸들러 등이 여기에 등록됨
app = FastAPI()


######################################################
# --- 요청 본문 처리 예제 ---
######################################################

# 1. POST 요청으로 Item 데이터 생성
# 함수의 파라미터 'item'에 위에서 정의한 Item 모델 타입을 지정합니다.
@app.post("/items/")
async def create_item(item: Item):  
    # FastAPI는 요청 본문(JSON)을 자동으로 파싱한 뒤
    # Item 모델로 변환 + 검증까지 수행합니다.
    # 검증 실패 시, 함수는 실행조자 되지 않고 422 에러 반환

    print(f"아이템 이름: {item.name}")
    print(f"아이템 설명: {item.description}")
    print(f"아이템 가격: {item.price}")
    print(f"아이템 세금: {item.tax}")

    # Pydantic 모델 객체를 그대로 반환하면 FastAPI가 자동으로 JSON으로 변환해줍니다.
    # 하지만 가공이 필요할 경우 dict로 변환해서 처리하는 것이 일반적
    # Pydantic V2 방식: model_dump() (이전 버전: item.dict())
    item_dict = item.model_dump()


    # 만약 세금 정보가 있다면 가격에 세금을 더해봅시다.
    # if item.tax:
    # → tax가 None 이거나 0.0 이면 False로 평가됨
    # 즉, tax=0.0 인 경우 이 블록은 실행되지 않는다는 점이 포인트
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})

    # 반환값은 dict → FastAPI가 JSON Response로 직렬화
    return item_dict


# 2. PUT 요청으로 Item 데이터 업데이트 (경로 매개변수 + 요청 본문)
# item_id 경로 매개변수와 item 요청 본문을 함께 받습니다.
@app.put("items/{item_id}")
async def update_item(item_id: int, item: Item):    
    # item_id는 경로에서, item은 본문에서 옵니다.
    #
    # item_id:
    # URL 경로에서 추출되어 자동으로 int 변환 및 검증
    # 숫자가 아니면 422 에러 발생
    #
    # item:
    # 요청 본문(JSON)을 Item 모델로 변환한 결과

    print(f"업데이트 할 아이템 ID: {item_id}")
    print(f"업데이트 내용: {item.model_dump()}")

    # 실제 서비스라면 여기서 DB 업데이트 로직이 들어감
    return {"item_id": item_id, "updated_item_data": item.model_dump()}


# 3. 요청 본문 + 경로 매개변수 + 쿼리 매개변수 혼합 사용
@app.put("/items-complex/{item_id}")
async def update_item_complex(
    item_id: int,               # 경로 매개변수 (/items-complex/3)
    item: Item,                 # 요청 본문 (JSON Body)
    q: Optional[str] = None     # 선택적 쿼리 매개변수 (?q=search)
):
    # FastAPI는 파라미터의 위치로 역할을 구분함
    # - 경로에 있으면 Path Parameter
    # - BaseModel이면 Request Body
    # - 기본값이 있으면 Query Parameter

    # **dict 병합 문법
    # result는 item_id + item 본문 애용을 하나의 응답으로 합칩 구조
    result = {"item_id": item_id, **item.model_dump()}  # 경로 매개변수와 본문 내용을 합침

    
    # 쿼리 매개변수 q가 있다면 결과에 추가
    if q:
        result.update({"query_param_q": q})
    
    print(f"아이템 ID: {item_id}")
    print(f"업데이트 내용: {item.model_dump()}")
    
    if q:
        print(f"쿼리 파라미터 q: {q}")

    return result