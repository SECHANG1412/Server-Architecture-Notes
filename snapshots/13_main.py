from fastapi import FastAPI, Response, Cookie, status
from typing import Optional

app = FastAPI()


##################################################
# --- 헤더 관리 예제 ---
##################################################

# 클라이언트가 GET 방식으로 "/headers/set-custom" 주소에 요청하면 아래 함수를 실행하도록 등록한다.
@app.get("/headers/set-custom")
async def set_custom_header(response: Response):
    response.headers["X-Custom-Header-1"] = "Hello from custom header!" # 서버가 클라이언트에게 보내는 응답 헤더에 "X-Custom-Header-1"이라는 이름과 값을 추가
    response.headers["X-Another-Header"] = "FastAPI is awesome"         # 서버가 클라이언트에게 보내는 응답 헤더에 "X-Another-Header"라는 이름과 값을 추가한다
    response.headers["Server"] = "My Custom FastAPI Server"             # 서버가 클라이언트에게 보내는 응답 헤더에 "Server"라는 이름과 값을 추가한다

    # 응답 본문(body)으로 메시지를 담은 JSON 데이터를 클라이언트에게 반환한다
    return {
        "message": "Check the response headers in your browser's developer tools!"
    }


##################################################
# --- 쿠키 관리 예제 ---
##################################################

# 클라이언트가 POST 방식으로 "/cookies/set-simple" 주소에 요청하면 아래 함수를 실행하도록 등록한다
@app.post("/cookies/set-simple")
async def set_simple_cookie(response: Response):
    response.set_cookie(key="simple_cookie", value="hello_fastapi") # 클라이언트 브라우저에 "simple_cookie"라는 이름과 값을 가진 쿠키를 저장하도록 설정한다

    # 쿠키가 설정되었음을 알리는 메시지를 JSON 형태로 반환한다
    return {
        "message": "Simple cookie has been set. Close your browser and see if it persists!"
    }


# 클라이언트가 POST 방식으로 "/cookies/set-options" 주소에 요청하면 아래 함수를 실행하도록 등록한다
@app.post("/cookies/set-options")
async def set_cookie_with_options(response: Response):

    # 여러 옵션을 포함하여 "user_session_id"라는 이름의 쿠키를 클라이언트 브라우저에 저장하도록 설정한다
    response.set_cookie(
        key="user_session_id",      # 쿠키의 이름을 설정
        value="abc123xyz789",       # 쿠키에 저장할 값을 설정
        max_age=60 * 60 * 24 * 7,   # 쿠키가 유지되는 시간을 초 단위로 설정 (7일)
        path="/",                   # 쿠키가 모든 경로에서 사용되도록 설정
        # domain=".example.com",    # 특정 도메인에서만 쿠키를 사용하도록 설정할 수 있지만 현재는 사용하지 않는다
        secure=True,                # HTTPS 연결에서만 쿠키가 전송되도록 설정
        httponly=True,              # 자바스크립트에서 쿠키에 접근하지 못하도록 설정
        samesite="lax"              # 다른 사이트 요청 시 쿠키 전송 규칙을 설정
    )

    # 옵션이 포함된 쿠키가 설정되었음을 알리는 메시지를 반환한다
    return {
        "message": "Cookie 'user_session_id' ser with options!"
    }


# 클라이언트가 GET 방식으로 "/cookies/get" 주소에 요청하면 아래 함수를 실행하도록 등록한다
@app.get("/cookies/get")
async def get_cookie_value(
    # 요청에 포함된 "user_session_id" 쿠키 값을 가져오고, 없으면 None으로 설정한다
    user_session_id: Optional[str] = Cookie(default=None)
):
    # 쿠키 값이 존재하는 경우 실행한다
    if user_session_id:
        # 서버 콘솔에 전달받은 쿠키 값을 출력한다
        print(f"Received user_session_id cookie: {user_session_id}")
        # 클라이언트에게 쿠키 값을 JSON 형태로 반환한다
        return {
            "cookie_value": user_session_id
        }
    else:
        # 쿠키가 없을 경우 서버 콘솔에 메시지를 출력한다
        print("user_session_id cookie not found.")
        # 쿠키가 없다는 메시지를 클라이언트에게 반환한다
        return {
            "message": "Cookie 'user_session_id' not found in request."
        }


# 클라이언트가 DELETE 방식으로 "/cookies/delete" 주소에 요청하면 아래 함수를 실행하도록 등록한다
# 응답 상태 코드를 204(No Content)로 설정한다
@app.delete("/cookies/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_cookie(response: Response):

    # 서버 콘솔에 쿠키 삭제 동작이 실행되었음을 출력한다
    print("Deleting user_session_id cookie.")

    # 쿠키를 삭제하려면, 동일한 key, path, domain으로 만료 시간을 과거로 설정하거나 max_age=0 으로 설정

    # 클라이언트 브라우저에 저장된 "user_session_id" 쿠키를 삭제하도록 설정한다
    response.delete_cookie(key="user_session_id", path="/", domain=None)

    # 쿠키를 즉시 만료시키는 다른 방법을 예시로 남겨둔다
    # 또는 response.set_cookie(key="user_session_id", value="", max_age=0)

    # 응답 본문 없이 요청 처리를 끝낸다
    return None