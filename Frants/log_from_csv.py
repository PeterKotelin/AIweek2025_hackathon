import csv,os,json,ast,random
from log import *
from datetime import datetime,timedelta
import log
from tqdm import tqdm


def main():
    scan_info = get_csv(os.path.join(os.path.dirname(__file__),"logs","area_and_trash_info.csv"))
    box_info = get_csv(os.path.join(os.path.dirname(__file__),"logs","defects_info.csv"))
    print(len(scan_info),len(box_info))
    print(scan_info[:3])
    print(box_info[:3])

    for i in range(len(box_info)):
        box_info[i]["defects"] = ast.literal_eval(box_info[i]["defects"])

    print(box_info[3])
    
    # BD init
    global cursor
    cursor = connect_to_bd()
    print("Connected to BD")
    create_Images("Images",[("scan_id","SERIAL",True),
                            ("area","FLOAT4",False),
                            ("flawed","INT",False),
                            ("date","DATE",False),
                            ("time","TIME",False),
                            ("person","VARCHAR(50)",False),
                            ],cursor = cursor)
    print("Images created")
    create_Boxes(cursor = cursor)

    print("tqdm should start any second")
    # Transfer
    for scan_i,data in tqdm(enumerate(zip(scan_info,box_info),start=1),colour="red"):
        scan,boxes = data
        date = random_date()
        time = random_time()
        person = randoom_person()
        save_scan(scan["defected_area"],scan["is_trash"],date,time,person,cursor = cursor)
        for box in boxes["defects"]:
            save_box(scan_i,box[0],box[1][0],box[1][1],box[1][2],box[1][3],cursor = cursor)

    get_table("Boxes",cursor = cursor)
    print(cursor.fetchall())
    get_table("Images",cursor = cursor)
    print(cursor.fetchall())

    log.conn.commit()
    cursor.close()


def get_csv(path:os.PathLike):
    result = []
    with open(path,"r") as file:
        fieldnames = next(file).split(",")
        fieldnames[-1] = fieldnames[-1].strip("\n")
        reader = csv.DictReader(file,fieldnames)
        for line in reader:
            result.append(line)
    
    return result

def random_date():
    return datetime.now().date() - timedelta(days=random.randint(0,30))

def random_time():
    return (datetime.now() + timedelta(seconds=random.randint(0,86_400))).time()

def randoom_person():
    people = [
        "Оператор 1",
        "Оператор 2",
        "Оператор 3",
        "Оператор 4",
        "Оператор 5",
        "Оператор 6",
        "Оператор 7",
        ]
    return random.choice(people)

if __name__=="__main__":
    main()