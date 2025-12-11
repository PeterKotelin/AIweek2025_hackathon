from PIL import Image
import os

def dark_box(path:os.PathLike,boxes:list[tuple[int]]):
    image = Image.open(path)
    # print(image.getpixel((100,100)))
    average = avg_good(image,boxes=boxes)
    minimum = min_bad(image,boxes=boxes)

    # print(f"{average:=}")
    # print(f"{minimum:=}")

    return (average - minimum) > 50

def avg_good(img:Image.Image,boxes:list[tuple]):
    total = img.getpixel((0,0))[0]
    i = 1
    for x in range(1,img.width):
        for y in range(img.height):
            if not in_boxes((x,y),boxes):
                pixel = img.getpixel((x,y))[0]
                total += pixel
                i += 1
    
    return total/i

def min_bad(img:Image.Image,boxes:list[tuple]):
    min_value = 255
    for x in range(1,img.width):
        for y in range(img.height):
            if in_boxes((x,y),boxes):
                pixel = img.getpixel((x,y))[0]
                min_value = min(min_value,pixel)
    
    return min_value

def in_boxes(coords:tuple[int],boxes:list[tuple[int]]):
    for box in boxes:
        if coords[0] > box[0] and coords[0] < box[2]:
            if coords[1] > box[1] and coords[1] < box[3]:
                return True
    return False


if __name__=="__main__":
    result = dark_box(os.path.join(os.path.dirname(__file__),"inclusion_141.jpg"),[(20,0,130,200)])
    print(result)