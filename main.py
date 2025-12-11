import base64
import random
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Literal, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse

# Константы
ROOT = Path('.')
FALLBACK_IMAGE = ROOT / 'maxresdefault_classify.jpg'
GRAPHS_DIR = ROOT / 'static' / 'graphs'

app = FastAPI(title='Metrics & Classification API')


# --- Утилиты ---------------------------------------------------------------

def read_image_bytes(path: Path) -> Optional[bytes]:
    """Безопасно возвращает байты по пути, либо None, если файла нет."""
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


# --- Классификация (симуляция) -------------------------------------------

def classify_image_sync(file: Optional[UploadFile] = None) -> tuple[Optional[bytes], List[str]]:
    """
    Симулирует работу функции классификации.
    Игнорирует переданный файл и возвращает байты из файла
    `maxresdefault_classify.jpg` в корне проекта и массив текстов.

    image_bytes = image_path.read_bytes()
    texts = ["классификация выполнена", "пример результата"]
    return image_bytes, texts


# --- Endpoints ------------------------------------------------------------

@app.get('/')
def read_root() -> dict:
    """Простой health-check endpoint."""
    return {"It": "works"}


@app.post('/api/classify')
async def classify_image(file: UploadFile = File(...)) -> JSONResponse:
    """
    Принимает загруженную картинку (не обрабатывает её).
    Вызывает `classify_image_sync`, получает image bytes и список текстов.
    Возвращает JSON с base64-картинкой и текстовым массивом.
    """
    # читаем (и игнорируем) содержимое загруженного файла, чтобы освободить поток
    await file.read()

    image_bytes, texts = classify_image_sync(file)
    if image_bytes is None:
        return JSONResponse({
            "success": False,
            "message": f"Файл {FALLBACK_IMAGE.name} не найден",
            "texts": texts
        }, status_code=404)

    return JSONResponse({
        "success": True,
        "texts": texts,
        # Отдаём изображение как base64 в JSON (клиент может декодировать)
        "image_data": base64.b64encode(image_bytes).decode('ascii'),
        "image_filename": FALLBACK_IMAGE.name,
        "image_content_type": "image/jpeg",
    })
