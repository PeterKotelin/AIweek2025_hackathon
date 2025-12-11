import io
import base64
import random
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Literal, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse

from Frants import log
from features.heat_map.heat_map import HeatMapVisualization

# Константы
ROOT = Path('.')
FALLBACK_IMAGE = ROOT / 'maxresdefault_classify.jpg'
GRAPHS_DIR = ROOT / 'static' / 'graphs'

app = FastAPI(title='Metrics & Classification API')

cursor = log.connect_to_bd()


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

    Возвращаемое значение: (image_bytes или None, список строк)
    """
    image_bytes = read_image_bytes(FALLBACK_IMAGE)
    if image_bytes is None:
        return None, [f"файл '{FALLBACK_IMAGE.name}' не найден"]

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


DamageClass = Literal[
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled_in_scale",
    "scratches",
]


@dataclass
class MetricsItem:
    date: str
    count: int


def generate_counts(days: int, cls: Optional[str]) -> List[MetricsItem]:
    """
    Генерирует псевдо-статистику по дням для указанного класса дефекта.
    """
    base_map = {
        None: 8,
        "crazing": 12,
        "inclusion": 6,
        "patches": 7,
        "pitted_surface": 10,
        "rolled_in_scale": 5,
        "scratches": 9,
    }
    variance_map = {
        None: 4,
        "crazing": 5,
        "inclusion": 3,
        "patches": 3,
        "pitted_surface": 4,
        "rolled_in_scale": 2,
        "scratches": 4,
    }
    base = base_map.get(cls, base_map[None])
    var = variance_map.get(cls, variance_map[None]) or 1

    items: List[MetricsItem] = []
    for i in range(days):
        d = date.today() - timedelta(days=days - 1 - i)
        # простой сезонный сдвиг: немного выше в начале/конце недели
        weekday = d.weekday()
        seasonal = (2 if weekday in (0, 1) else 0) + (3 if weekday in (4, 5) else 1)
        pseudo_rand = ((d.year + d.month + d.day + (hash(cls) if cls else 0)) % max(1, var))
        count = max(0, base + seasonal + pseudo_rand)
        items.append(MetricsItem(date=d.isoformat(), count=count))
    return items


@app.get('/api/metrics')
def get_metrics(class_: Optional[DamageClass] = Query(None, alias='class'), 
                start_date_: Optional[str] = Query(None, alias='start_date'),
                end_date_: Optional[str] = Query(None, alias='end_date')) -> List[Dict[str, str]]:
    """
    Возвращает список словарей с полями date и count за последние 30 дней.
    Параметр `class` — необязательный query-параметр для фильтрации (alias работает как 'class').
    """
    data = log.get_data_for_time_stat(cursor=cursor,
                                      start_date=start_date_,
                                      end_date=end_date_,
                                      class_type=class_)
    return data


BASE_CATEGORIES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled_in_scale",
    "scratches",
]


def build_fixed_payload() -> dict:
    """Фиксированный пример возвращаемых категорий с дефектами."""
    return {
        "crazing": 11,
        "crazing_defect": 2,
        "inclusion": 3,
        "inclusion_defect": 1,
        "patches": 8,
        "patches_defect": 3,
        "pitted_surface": 5,
        "pitted_surface_defect": 2,
        "rolled_in_scale": 7,
        "rolled_in_scale_defect": 1,
        "scratches": 9,
        "scratches_defect": 4,
    }


def build_random_payload(seed: Optional[int] = None) -> dict:
    """Генерирует случайные метрики по категориям (опционально с seed для детерминированности)."""
    if seed is not None:
        random.seed(seed)
    payload: Dict[str, int] = {}
    for cat in BASE_CATEGORIES:
        base = random.randint(1, 20)
        defect = max(0, int(base * random.uniform(0.05, 0.5)))
        payload[cat] = base
        payload[f"{cat}_defect"] = defect
    return payload


@app.get('/api/metrics/categories')
def get_categories() -> JSONResponse:
    """
    Возвращает набор метрик по категориям.
    mode=random -> случайные значения (seed опционален), иначе фиксированные значения.
    """
    data = log.get_defect_count(cursor=cursor)
    return JSONResponse(content=data)


SAMPLE_NAMES = [
    "Иванов И.И.", "Петров П.П.", "Сидоров С.С.", "Кузнецов К.К.",
    "Смирнова А.А.", "Попов О.О.", "Лебедев Л.Л.", "Козлова К.К.",
    "Николаев Н.Н.", "Морозова М.М."
]


def build_random_workers(size: int = 8) -> List[Dict[str, Any]]:
    """Генерирует список работников {name: str, count: int}.

    - name: строка (Ф.И.О.)
    - count: случайное целое количество
    """
    workers: List[Dict[str, Any]] = []
    for i in range(size):
        name = SAMPLE_NAMES[i % len(SAMPLE_NAMES)]
        if i >= len(SAMPLE_NAMES):
            # при нехватке уникальных имён добавляем индекс
            name = f"{name} #{i + 1}"
        count = random.randint(10, 300)
        workers.append({"name": name, "count": count})
    return workers


@app.get('/api/metrics/workers')
def get_workers() -> List[Dict[str, Any]]:
    """Возвращает массив работников. Параметр size контролирует количество объектов."""
    data = log.get_person_data(cursor=cursor)
    return data


@app.get('/api/metrics/graph')
def get_graph(class_: Optional[DamageClass] = Query(None, alias='class')):
    """
    Возвращает файл графика для указанного класса из `static/graphs`.
    Если файл не найден, отдаёт fallback-изображение из корня проекта.
    """
    heatmap_diagram = HeatMapVisualization()
    data = log.get_data_for_heatmap(class_,cursor=cursor)
    buf = heatmap_diagram.visualize_heatmap(data)


    return StreamingResponse(buf, media_type="image/png")


