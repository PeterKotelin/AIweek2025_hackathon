import csv,os
from datetime import datetime

dir_name = os.path.dirname(__file__)

def main():
    name = str(datetime.now()).split(" ")[0] + ".csv"
    path = os.path.join(dir_name,"logs",name)
    if name not in os.listdir(os.path.join(dir_name,"logs")):
        make_log(path)

    new_line = {
        "id": 0,
        "defects": [("asdf",(0,0,100,100)),("asdf",(50,50,150,1500))],
        "defected_area": 0.3,
        "is_trash": True
    }

    log_line(path,new_line)


def make_log(name:str):
    print("New log started")
    with open(name,"w",encoding="utf-8",newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["id","defects","defected_area","is_trash"]
            )
        writer.writeheader()


def log_line(path,line:dict):
    print(line)
    with open(path,"a",newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["id","defects","defected_area","is_trash"]
        )
        writer.writerow(line)

if __name__=="__main__":
    main()