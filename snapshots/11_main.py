from fastapi import FastAPI, status
from fastapi.responses import (
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    JSONResponse,
)

app = FastAPI()

########################################################
# --- 다양한 Response 클래스 사용 예제 ---
########################################################
# 이 아래부터는 "서버가 어떤 형태로 응답할 수 있는지"를 하나씩 보여주는 예제들

# 1. HTML 응답 반환하기
# "/html" 주소로 GET 요청이 오면 실행됨
# response_class=HTMLResponse → 기본 응답 형식을 HTML로 지정
@app.get("/html", responses_class=HTMLResponse)     # response_class를 HTMLResponse로 지정
async def read_html():
    # HTML 문서를 문자열 형태로 작성
    # 브라우저는 이 문자열을 "웹 페이지"로 인식함
    html_content = """
    <html>
        <head>
            <title>FastAPI HTML Response</title>
            <style>
                body { font-family: sans-serif; }
                h1 { color: green; }
            </style>
        </head>
        <body>
            <h1>Hello from FastAPI! 👋</h1>
            <p>This is an HTML response.</p>
        </body>
    </html>
    """
    # HTML 문자열을 그대로 return
    # FastAPI는 response_class=HTMLResponse 설정을 보고
    # "아, 이건 HTML이구나" 하고 HTMLResponse로 감싸서 브라우저에 보냄
    return html_content



# 2. PlainText 응답 반환하기
# "/text" 주소로 GET 요청이 오면 실행됨
@app.get("/text")
async def read_text():
    # PlainTextResponse 객체를 직접 만들어서 반환
    # → "이건 그냥 글자야!" 라고 명확하게 알려주는 방식
    return PlainTextResponse(
        content="This is a plain text response from FastAPI.", 
        status_code=200     # HTTP 200 = 정상 처리
    )


# 3. Redirect 응답 반환하기
# "/redirect/docs" 주소로 오면 다른 주소로 이동시킴
@app.get("/redirect/docs")
async def redirect_to_docs():
    # RedirectResponse는 "여기 말고 저기로 가세요"라는 응답
    # /docs는 FastAPI의 자동 API 문서 페이지
    return RedirectResponse(
        url="/docs", 
        status_code=status.HTTP_307_TEMPORARY_REDIRECT  # 307: 요청 방식(GET/POST 등)을 유지한 채 잠시 이동
    )

# 외부 사이트로 이동시키는 예
@app.get("/redirect/external")
async def redirect_external():
    # 외부 URL로 리디렉션 (302 Found - 임시 리디렉션의 일반적인 코드)
    return RedirectResponse(
        url="<https://fastapi.tiangolo.com/>", 
        status_code=status.HTTP_302_FOUND     # 302: 가장 흔히 쓰이는 임시 이동 코드
    )



# 4. JSONResponse 명시적 사용 (기본 동작과 유사하지만, 직접 제어 가능)
# response_class=JSONResponse → 기본 응답 형식을 JSON으로 지정
@app.get("/json/custom", response_class=JSONResponse)   # response_class 사용 예시
async def read_custom_json():
    # 딕셔너리를 반환
    # FastAPI는 이걸 JSON 형태로 자동 변환
    return {
        "message": "This is a custom JSON response using response_class"
    }

# POST 요청 예제
# status_code=201 → "새로운 리소스가 생성되었음"
@app.post("/json/created", status_code=status.HTTP_201_CREATED) # 기본 상태 코드 지정
async def create_resource():
    # JSONResponse를 직접 반환
    # → 상태 코드, 헤더, 내용 등을 내가 직접 통제
    return JSONResponse(
        content={
            "resource_id": 123, 
            "status": "created"
        },
        status_code=status.HTTP_201_CREATED
        # 데코레이터에서 지정했지만
        # 여기서 다시 명시해도 문제 없음 (이 값이 최종 적용)
    )



# 5. response_class와 Response 객체 직접 반환 혼용 시
# 기본 응답은 PlainTextResponse
@app.get("/mixed-response", response_class=PlainTextResponse)   # 기본은 PlainText
async def mixed_response(return_html: bool = False):
    if return_html:
        # HTMLResponse 객체를 직접 반환하면 response_class보다 우선함
        return HTMLResponse(
            "<h1>This is HTML overridin PlainText</h1>"
        )
    else:
        # 문자열만 반환하면 response_class(PlainTextResponse)가 적용됨
        return "This is the default PlainText response."