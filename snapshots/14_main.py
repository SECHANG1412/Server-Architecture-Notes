import os, shutil, aiofiles
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, status

app = FastAPI()

# 업로드된 파일을 저장할 디렉토리 (없으면 생성)
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


#######################################################
# --- 파일 업로드 엔드포인트 정의 ---
#######################################################

# 1. 클라이언트가 POST 방식으로 작은 파일을 업로드하면 이 함수를 실행하도록 등록한다
@app.post("/files/upload-bytes/")
async def upload_small_file(
    # 업로드된 파일 전체를 bytes 형태로 받아서 file 변수에 저장한다
    file: bytes = File(..., description="Upload a small file as bytes")
):
    # 업로드된 파일의 전체 크기를 바이트 단위로 계산한다
    file_size = len(file)

    print(f"Received small file (bytes), size: {file_size} bytes")

    # 파일 크기가 1MB보다 크면 경고 메시지를 출력한다    
    if file_size > 1024 * 1024:
        print("Warning: File size is large for 'bytes' handling.")

    # 파일 크기와 처리 완료 메시지를 클라이언트에게 반환한다
    return {
        "file_size": file_size,
        "message": "File received as bytes."
    }



# 2. 클라이언트가 POST 방식으로 단일 파일을 업로드하면 이 함수를 실행하도록 등록한다
@app.post("/files/upload-single/")
async def upload_single_file(
    # UploadFile 타입으로 파일 정보를 받아 file 변수에 저장한다
    file: UploadFile = File(..., description="Upload a single file using UploadFile")
):
    print(f"Received file: {file.filename}")
    print(f"Content type: {file.content_type}")

    # 파일 이름에서 경로 정보를 제거하고 안전한 파일 이름을 만든다
    safe_filename = os.path.basename(file.filename or "uploaded_file") 

    # 저장할 파일의 전체 경로를 만든다
    destination = os.path.join(UPLOAD_DIR, safe_filename)

    print(f"Saving file to: {destination}")

    # 파일 저장 중 오류가 발생할 수 있으므로 예외 처리를 시작한다
    try:
        # 지정한 경로에 파일을 쓰기 모드로 비동기 방식으로 연다
        async with aiofiles.open(destination, 'wb') as out_file:
            # 파일 내용을 1MB씩 반복해서 읽는다
            while content := await file.read(1024 * 1024):    
                # 읽은 내용을 파일에 바로 기록한다
                await out_file.write(content)

    except Exception as e:
        print(f"File saving error: {e}")

        # 클라이언트에게 500 에러와 오류 메시지를 반환한다
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {e}"
        )
    
    finally:
        # 파일 정리 작업을 위한 위치이지만 현재는 아무 동작도 하지 않는다
        pass
    

    # 업로드된 파일 정보와 저장 경로를 클라이언트에게 반환한다
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "save_path": destination
    }



# 3. 클라이언트가 POST 방식으로 여러 개의 파일을 업로드하면 이 함수를 실행하도록 등록
@app.post("/files/upload-multiple/")
async def upload_multiple_files(
    # 여러 개의 UploadFile 객체를 리스트 형태로 받아 files 변수에 저장
    files: List[UploadFile] = File(..., description="Upload multiple files")
):
    # 저장 결과를 담을 빈 리스트를 만든다
    saved_files = []

    # 업로드된 파일을 하나씩 반복해서 처리
    for file in files:
        print(f"Processing file: {file.filename}")
        safe_filename = os.path.basename(file.filename or f"uploaded_file_{len(saved_files)}")  # 파일 이름이 없을 경우를 대비해 기본 이름을 설정
        destination = os.path.join(UPLOAD_DIR, safe_filename)                                   # 파일이 저장될 전체 경로를 만든다

        try:
            # 파일을 쓰기 모드로 비동기 방식으로 연다
            async with aiofiles.open(destination, 'wb') as out_file:
                # 파일 내용을 1MB씩 읽어서 저장
                while content := await file.read(1024 * 1024):
                    await out_file.write(content)
            saved_files.append({"filename": file.filename, "save_path": destination})           # 정상적으로 저장된 파일 정보를 리스트에 추가

        except Exception as e:
            print(f"Error saving {file.filename}: {e}")                         # 파일 저장 중 오류가 발생하면 서버 콘솔에 출력한다
            saved_files.append({"filename": file.filename, "error": str(e)})    # 오류가 발생한 파일 정보와 오류 내용을 리스트에 추가

    # 처리된 파일 개수와 상세 결과를 클라이언트에게 반환
    return {
        "message": f"{len(saved_files)} files processed.", 
        "details": saved_files
    }


# 4. 클라이언트가 파일과 함께 다른 폼 데이터를 업로드하면 이 함수를 실행하도록 등록
@app.post("/files/upload-with-form/")
async def upload_file_and_form(
    file: UploadFile = File(...),   # 업로드된 파일을 UploadFile 타입으로 받는다
    notes: Optional[str] = None     # 선택적으로 전달된 문자열 데이터를 notes 변수에 저장
):
    print(f"Received file: {file.filename}")    # 서버 콘솔에 업로드된 파일 이름을 출력

    # notes 값이 있으면 서버 콘솔에 출력
    if notes:
        print(f"Received notes: {notes}")

    safe_filename = os.path.basename(file.filename or "uploaded_file")  # 파일 이름을 안전하게 처리한다
    destination = os.path.join(UPLOAD_DIR, safe_filename)               # 파일이 저장될 경로를 만든다

    # 파일 정보와 메모 내용을 클라이언트에게 반환한다
    return {
        "filename": file.filename, 
        "notes": notes, 
        "save_path": "simulated_save"
    }