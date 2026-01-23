import os, mimetypes
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI()

# 다운로드할 파일들이 저장된 폴더 경로를 문자열로 지정
DOWNLOAD_DIR = "./downloadables/"   


#######################################################
# --- 기본 파일 다운로드 ---
#######################################################

# 사용 의도:
# 서버에 저장된 파일을 그대로 찾아서
# 이름이나 타입을 바꾸지 않고
# 가장 단순한 방식으로 다운로드시키기 위한 함수이다

# 클라이언트가 GET 방식으로 "/download/basic/{file_name}" 주소에 요청하면 
# 이 함수를 실행하도록 등록
@app.get("/download/basic/{file_name}")
async def download_basic(file_name: str):

    # 전달받은 파일 이름에서 경로 요소를 제거해 파일 이름만 남긴다
    safe_base_filename = os.path.basename(file_name)     

    # 다운로드 폴더 경로와 파일 이름을 합쳐 실제 파일 경로를 만든다           
    file_path = os.path.join(DOWNLOAD_DIR, safe_base_filename)      


    # 해당 경로에 실제 파일이 존재하지 않으면 실행
    if not os.path.isfile(file_path):

        # 서버 콘솔에 파일을 찾지 못했다는 메시지를 출력
        print(f"Error: File not found at {file_path}")  

        # 클라이언트에게 404 오류를 반환
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    

    # 요청한 파일 경로가 다운로드 폴더 바깥을 가리키는 경우 실행
    if not file_path.startswith(os.path.abspath(DOWNLOAD_DIR)):

        # 서버 콘솔에 접근 거부 메시지를 출력
        print(f"Error: Access denied to path {file_path}")  

        # 클라이언트에게 403 오류를 반환
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # 서버 콘솔에 제공할 파일 경로를 출력
    print(f"Serving file: {file_path}")     
    
    # 지정된 파일을 그대로 다운로드 응답으로 반환
    return FileResponse(path=file_path)



#######################################################
# --- 커스텀 파일 다운로드 ---
#######################################################

# 사용 의도:
# 서버 파일을 다운로드할 때
# 파일 이름을 바꾸거나
# 파일 타입을 명확히 지정해서
# 브라우저의 다운로드 동작을 제어하기 위한 함수이다

# 클라이언트가 GET 방식으로 "/download/custom/{file_name}" 주소에 요청하면 
# 이 함수를 실행하도록 등록
@app.get("/download/custom/{file_name}")
async def download_custom(file_name: str):

    # 전달받은 파일 이름에서 경로 요소를 제거
    safe_base_filename = os.path.basename(file_name)

    # 다운로드 폴더와 파일 이름을 합쳐 실제 파일 경로를 만든다
    file_path = os.path.join(DOWNLOAD_DIR, safe_base_filename)

    # 파일이 존재하지 않으면 실행
    if not os.path.isfile(file_path):
        # 클라이언트에게 404 오류를 반환
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # 파일 경로가 허용된 다운로드 폴더를 벗어나면 실행
    if not file_path.startswith(os.path.abspath(DOWNLOAD_DIR)):
        # 클라이언트에게 403 오류를 반환
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    

    # 파일 확장자를 기준으로 파일 타입을 추측
    media_type, _ = mimetypes.guess_type(file_path)

    # 파일 타입을 알 수 없을 경우 기본 타입을 설정
    if media_type is None:
        media_type = 'application/octect-stream'

    # 다운로드될 때 사용할 파일 이름을 새로 만든다
    download_filename = f"downloaded_{safe_base_filename}"

    # 서버 콘솔에 파일 정보와 다운로드 이름을 출력
    print(f"Serving file: {file_path} as {download_filename} with type {media_type}")

    # 파일 경로, 다운로드 이름, 파일 타입을 지정하여 다운로드 응답을 반환
    return FileResponse(
        path=file_path,
        filename=download_filename,
        media_type=media_type
    )


#######################################################
# --- 스트리밍용 가짜 데이터 생성 ---
#######################################################

# 사용 의도:
# 실제 파일이 없어도
# 서버에서 데이터를 조금씩 만들어
# 스트리밍 다운로드가 어떻게 동작하는지
# 테스트하기 위한 함수이다

# 가짜 데이터를 한 줄씩 만들어서 보내는 비동기 함수
async def fake_data_streamer():
    # 0부터 9까지 반복하면서 실행
    for i in range(10):
        # 한 줄의 문자열 데이터를 만들어 하나씩 반환
        yield f"Line {i+1}: Some data chunk\\n"


#######################################################
# --- 스트리밍 다운로드 ---
#######################################################

# 사용 의도:
# 파일이 디스크에 없어도
# 서버가 데이터를 실시간으로 생성하면서
# 클라이언트가 파일처럼 다운로드하게 만들기 위한 함수이다

# 클라이언트가 GET 방식으로 "/download/stream" 주소에 요청하면 이 함수를 실행하도록 등록
@app.get("/download/stream")
async def download_stream():

    # 가짜 데이터 스트림을 생성
    stream = fake_data_streamer()

    # 스트리밍 방식으로 데이터를 다운로드 응답으로 반환
    return StreamingResponse(

        # 스트림 데이터를 응답 내용으로 설정
        content=stream,
        
        # 응답 데이터 타입을 텍스트로 설정
        media_type="text/plain",
        
        # 브라우저가 파일로 저장하도록 헤더를 설정
        headers={"Content-Disposition": "attachment; filename=streamed_data.txt"}
    )