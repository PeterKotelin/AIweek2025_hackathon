import base64

from fastapi import FastAPI, UploadFile, File
from starlette.responses import JSONResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"It": "works"}


@app.post("/api/classify")
async def classify_image(file: UploadFile = File(...)):
    """
    Просто возвращает файл в base64 без анализа
    """
    contents = await file.read()

    return JSONResponse(content={
        "success": True,
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size_bytes": len(contents),
        "image_data": base64.b64encode(contents).decode("utf-8")
    })
