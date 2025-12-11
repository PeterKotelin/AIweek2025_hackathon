import torch
from PIL import ImageFont, ImageDraw
from torchvision import transforms
from torchvision.ops import batched_nms

# Путь к вашей модели
MODEL_PATH = 'best_model.pt'
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Классы дефектов
CLASSES = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
CLASS_TO_IDX = {cls: idx for idx, cls in enumerate(CLASSES)}
IDX_TO_CLASS = {idx: cls for cls, idx in CLASS_TO_IDX.items()}

# Цвета для разных классов (для отрисовки)
COLORS = ['red', 'green', 'blue', 'yellow', 'orange', 'purple']

# Трансформации
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

# Глобальная переменная для модели
model = None


# --------------------------------------------------------------------------
# ФУНКЦИИ
# --------------------------------------------------------------------------

def load_model_logic(model_path, device):
    """Загрузка модели (YOLO или PyTorch)"""
    try:
        from ultralytics import YOLO
        yolo_model = YOLO(model_path)
        print(f"✅ Загружена YOLO модель")
        return yolo_model
    except Exception:
        pass

    print(f"🔍 Загрузка как PyTorch модель...")
    try:
        import ultralytics
        from ultralytics.nn.tasks import DetectionModel
        torch.serialization.add_safe_globals([DetectionModel])
    except ImportError:
        pass

    try:
        loaded_model = torch.load(model_path, map_location=device, weights_only=False)
        loaded_model = loaded_model.to(device)
        loaded_model.eval()
        print(f"✅ PyTorch модель загружена")
        return loaded_model
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        return None


def apply_nms(boxes, labels, scores, iou_threshold=0.5):
    if len(boxes) == 0:
        return boxes, labels, scores
    keep_indices = batched_nms(boxes, scores, labels, iou_threshold)
    return boxes[keep_indices], labels[keep_indices], scores[keep_indices]


def predict_image(model, image_pil, device='cpu', conf_thresh=0.2, nms_thresh=0.1):
    w, h = image_pil.size

    # --- YOLO ---
    if hasattr(model, 'predict') and callable(model.predict):
        results = model.predict(image_pil, conf=conf_thresh, iou=nms_thresh, verbose=False)
        boxes, labels, scores = [], [], []
        if results:
            r = results[0]
            if hasattr(r, 'boxes'):
                boxes = r.boxes.xyxy.cpu().numpy().tolist()
                labels = r.boxes.cls.cpu().numpy().astype(int).tolist()
                scores = r.boxes.conf.cpu().numpy().tolist()
        return boxes, labels, scores

    # --- PyTorch ---
    else:
        img_tensor = image_pil.convert('L')
        input_tensor = transform(img_tensor).unsqueeze(0).to(device)

        with torch.no_grad():
            predictions = model(input_tensor)

        if not predictions:
            return [], [], []

        pred = predictions[0]
        mask = pred['scores'] > conf_thresh
        f_boxes = pred['boxes'][mask]
        f_labels = pred['labels'][mask]
        f_scores = pred['scores'][mask]

        nms_boxes, nms_labels, nms_scores = apply_nms(
            f_boxes, f_labels, f_scores, iou_threshold=nms_thresh
        )

        final_boxes = []
        final_labels = []
        final_scores = []

        for box, label, score in zip(nms_boxes, nms_labels, nms_scores):
            xmin, ymin, xmax, ymax = box.cpu().numpy()
            xmin = max(0, min(xmin, w - 1))
            ymin = max(0, min(ymin, h - 1))
            xmax = max(xmin + 1, min(xmax, w))
            ymax = max(ymin + 1, min(ymax, h))

            final_boxes.append([float(xmin), float(ymin), float(xmax), float(ymax)])
            final_labels.append(int(label.item()))
            final_scores.append(float(score.item()))

        return final_boxes, final_labels, final_scores


def draw_boxes_on_image(image_pil, boxes, labels, scores):
    """Рисует боксы на изображении (уменьшенный текст и рамка)"""
    # Конвертируем в RGB, чтобы можно было рисовать цветные рамки (даже если исходник ч/б)
    draw_img = image_pil.convert("RGB")
    draw = ImageDraw.Draw(draw_img)

    # Более маленький шрифт
    try:
        font = ImageFont.truetype("arial.ttf", 12)  # было 16
    except IOError:
        font = ImageFont.load_default()

    for box, label, score in zip(boxes, labels, scores):
        x1, y1, x2, y2 = box
        class_name = IDX_TO_CLASS.get(label, "unknown")

        # Выбор цвета по индексу класса
        color = COLORS[label % len(COLORS)]

        # Более тонкая рамка (width=1 или 2 вместо 3)
        draw.rectangle([x1, y1, x2, y2], outline=color, width=1)

        # Текст с подложкой
        text_caption = f"{class_name} {int(score * 100)}%"

        # Вычисляем размер текста (bbox)
        left, top, right, bottom = draw.textbbox((x1, y1), text_caption, font=font)

        # Меньший отступ подложки
        padding = 2  # было по сути ~5
        draw.rectangle(
            (left, top - padding, right, bottom + padding),
            fill=color
        )
        # Сам текст
        draw.text((x1, y1 - padding), text_caption, fill="white", font=font)

    return draw_img
