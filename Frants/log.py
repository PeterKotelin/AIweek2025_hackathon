import psycopg2
import sys,json
from datetime import datetime

def main():
    # Connection to DB
    global cursor
    cursor = connect_to_bd()
    print(type(cursor))

    try:
        if sys.argv[1] == "d":
            delete_db("Boxes",cursor = cursor)
            delete_db("Images",cursor = cursor)
            conn.commit()
            cursor.close()
            sys.exit()
    except IndexError:
        pass
    
    # Creates tables if needed
    get_tables(cursor = cursor)
    print(cursor.fetchall())
    create_Images("Images",[("scan_id","SERIAL",True),
                            ("area","FLOAT4",False),
                            ("flawed","INT",False),
                            ("date","DATE",False),
                            ("time","TIME",False),
                            ("person","VARCHAR(50)",False),
                            ],cursor = cursor)
    create_Boxes(cursor = cursor)

    # get_table("Boxes",cursor = cursor)
    # print(cursor.fetchall())
    # get_table("Images",cursor = cursor)
    # print(cursor.fetchall())

    # save_scan(0.2,1,datetime.now().date(),datetime.now().time(),cursor = cursor)
    # get_table("Images",cursor = cursor)
    # print(cursor.fetchall())

    # save_box(1,"scrach",0,0,150,150,cursor = cursor)
    # get_table("Boxes",cursor = cursor)
    # print(cursor.fetchall())


    # print(get_data_for_heatmap("asdf",cursor = cursor))

    print(get_data_for_time_stat())
    print(get_defect_count())
    print(get_person_data())

    # Saves the DB and exits
    conn.commit()
    cursor.close()


def connect_to_bd():
        try:
            global conn
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="asdf",
                host="localhost",
                port=5432
            )
            print("Connected to PostgreSQL successfully!")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
        
        cursor = conn.cursor()

        return cursor

def execute(func):
    def wrapper(*args,**kwargs):
        query = func(*args,**kwargs)
        print(f"executing:\n{query}")
        result = kwargs["cursor"].execute(query)
    return wrapper

@execute
def get_table(table_name:str,*args,**kwargs):
    if not args:
        return f"SELECT * FROM {table_name}"
    
    query = f"SELECT * FROM {table_name} WHERE "
    for arg in args:
        query += f"{arg[0]} = '{arg[1]}' AND"

    return query.strip(" AND")

@execute
def create_Images(name:str,args:list[tuple[str]],**kwargs):
    query =  f"""CREATE TABLE IF NOT EXISTS {name} ("""
    for item in args:
        if item[2]:
            query += f"\n{item[0]} {item[1]} PRIMARY KEY,"
        else:
            query += f"\n{item[0]} {item[1]} NOT NULL,"

    return query.strip(",") + ")"

@execute
def create_Boxes(**kwargs):
    return """CREATE TABLE IF NOT EXISTS Boxes (
        box_id SERIAL PRIMARY KEY,
        class_type VARCHAR(50) NOT NULL,
        x_min INT4 NOT NULL,
        y_min INT4 NOT NULL,
        x_max INT4 NOT NULL,
        y_max INT4 NOT NULL,
        scan_id INT,
        CONSTRAINT scan_serial
            FOREIGN KEY (scan_id)
            REFERENCES Images (scan_id)
            ON DELETE CASCADE
            ON UPDATE NO ACTION
    )"""


@execute
def clear_db(table_name:str,**kwargs):
    return f"""DELETE FROM {table_name}"""

@execute
def delete_db(table_name:str,**kwargs):
    return f"""DROP TABLE IF EXISTS {table_name}"""

@execute
def get_tables(**kwargs):
    return """SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"""

@execute
def save_scan(area:float,trash:bool,date,time,person,**kwargs):
    return f"INSERT INTO Images (area, flawed, date, time, person) VALUES ({area}, {trash}, '{date}', '{time}', '{person}');"

@execute
def save_box(scan_id:int, class_type:str, x_min:int, y_min:int, x_max:int, y_max:int,**kwargs):
    return f"INSERT INTO Boxes (scan_id, class_type, x_min, y_min, x_max, y_max) VALUES ({scan_id}, '{class_type}', {x_min}, {y_min}, {x_max}, {y_max});"

def get_data_for_heatmap(class_type:str|None = None,**kwargs):
    if class_type:
        get_table("Boxes",("class_type",class_type),cursor = kwargs["cursor"])
    else:
        get_table("Boxes",cursor = kwargs["cursor"])

    boxes = cursor.fetchall()

    return boxes
    

def get_data_for_time_stat(start_date:str|None = None,end_date:str|None = None, class_type:str|None = None):
    """Result:
[
  { "date": "2025-12-01", "count": 12 },
  { "date": "2025-12-02", "count": 8 },
  { "date": "2025-12-03", "count": 15 }
]"""
    sql_data_for_time_stat(start_date="2025-11-23",end_date="2025-12-11",class_type="inclusion",cursor = cursor)
    data = cursor.fetchall()
    result = []
    for line in data:
        result.append({
            "date":str(line[0]),
            "count":line[1]
        })
    return json.dumps(result)

@execute
def sql_data_for_time_stat(start_date:str|None = None,end_date:str|None = None, class_type:str|None = None, **kwargs):
    if start_date and end_date:
        if class_type:
            return f"""
SELECT date, count(*) FROM Boxes
JOIN Images ON Boxes.scan_id = Images.scan_id
WHERE date < '{end_date}' AND date > '{start_date}' AND Boxes.class_type = '{class_type}'
GROUP BY Images.date
"""
        else:
            return f"""
SELECT date, count(*) FROM Boxes
JOIN Images ON Boxes.scan_id = Images.scan_id
WHERE date < '{end_date}' and date > '{start_date}'
GROUP BY Images.date
"""
    if class_type:
        return f"""
SELECT date, count(*) FROM Boxes
JOIN Images ON Boxes.scan_id = Images.scan_id
WHERE class_type = '{class_type}'
GROUP BY Images.date
"""     
    return f"""
SELECT Images.date, count(*) FROM Boxes
JOIN Images ON Boxes.scan_id = Images.scan_id
GROUP BY Images.date
"""

def get_defect_count():
    """{
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
  "scratches_defect": 4
}"""
    sql_defect_count(failiure=True,cursor=cursor)
    data_fail = cursor.fetchall()
    sql_defect_count(failiure=False,cursor=cursor)
    data_good = cursor.fetchall()
    data_good = dict(data_good)
    for i in range(len(data_fail)):
        data_fail[i] = list(data_fail[i])
        data_fail[i][0] = data_fail[i][0] + "_defect"
        data_fail[i] = tuple(data_fail[i])
    
    data_fail = dict(data_fail)

    data_good.update(data_fail) 

    return data_good
    

@execute
def sql_defect_count(failiure:bool|None = None, **kwargs):
    if failiure:
        return f"""
SELECT class_type,count(*) FROM Boxes
JOIN Images ON Boxes.scan_id = Images.scan_id
WHERE Images.flawed = {int(failiure)}
GROUP BY class_type
"""
    return f"""
SELECT class_type,count(*) FROM Boxes
GROUP BY class_type
"""

def get_person_data(): 
    """[
    { "name": "Иванов И.И.", "count": 120 },
    { "name": "Петров П.П.", "count": 95 },
    { "name": "Сидоров С.С.", "count": 78 }
    ]"""
    sql_person_data(cursor = cursor)
    data = cursor.fetchall()
    result = []
    for line in data:
        result.append({
            "name": line[0],
            "count": line[1],
        })
    return result


@execute
def sql_person_data(**kwargs):
    return f"""
SELECT person, count(*) FROM Images
GROUP BY person
"""


if __name__=="__main__":
    main()