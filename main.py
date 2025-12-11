import base64
from pathlib import Path
from fastapi import FastAPI, UploadFile, File
from starlette.responses import JSONResponse

app = FastAPI()


@app.get("/")
def read_root():
    return {"It": "works"}


def classify_image_sync(file: UploadFile):
    # Читаем картинку из корня проекта
    image_path = Path("maxresdefault_classify.jpg")
    if not image_path.exists():
        return None, ["файл 'maxresdefault_classify.jpg' не найден"]

    image_bytes = image_path.read_bytes()
    texts = ["классификация выполнена", "пример результата"]
    return image_bytes, texts


@app.post("/api/classify")
async def classify_image(file: UploadFile = File(...)):
    """
    Просто возвращает файл в base64 без анализа
    """
    contents = await file.read()

    image_bytes, texts = classify_image_sync(file)

    if image_bytes is None:
        return JSONResponse(content={
            "success": False,
            "message": "Файл из корня проекта не найден",
            "texts": texts
        }, status_code=404)

    return JSONResponse(content={
        "success": True,
        "texts": texts,
        "image_data": base64.b64encode(image_bytes).decode("utf-8"),
        "image_filename": "maxresdefault_classify.jpg",
        "image_content_type": "image/jpeg"
    })
