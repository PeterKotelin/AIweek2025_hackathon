import csv,os
from PIL import Image,ImageDraw


def main():
    image_height = 200
    image_width = 200
    # os.path.dirname(__file__),"archive","NEU-DET","train","images","inclusion","inclusion_80.jpg")
    image = Image.open(
        os.path.join(os.path.dirname(__file__),"archive","NEU-DET","train","images","inclusion","inclusion_80.jpg"),
    )
    print(image.width,image.height)

    boxes = get_boxes()
    draw = ImageDraw.Draw(image)

    for box in boxes:
        draw.rectangle(box,outline="red",width=2)
    
    
    print(f"Total bad area: {total_percent(boxes)*100}%")
    
    image.show("shit")

def percent_per_box(box:tuple[int]) -> float:
    return ((box[2] - box[0])*(box[3] - box[1]))/(200*200)

def total_percent(boxes:tuple[tuple[int]]) -> float:
    result = 0
    for box in boxes:
        result += percent_per_box(box)
    return result

def smart_area(boxes:tuple[tuple[int]]):
    for i,box1 in enumerate(boxes):
        for box2 in boxes[i:]:
            pass

def get_boxes():
    result = (
        (0,0,100,100),
        (100,100,150,150),
        (150,160,199,198),
        (120,130,130,140),
    )
    return result


if __name__=="__main__":
    main()