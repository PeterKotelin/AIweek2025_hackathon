import psycopg2
import sys

def main():
    # Connection to DB
    global cursor
    cursor = connect_to_bd()
    print(type(cursor))

    try:
        if sys.argv[1] == "d":
            delete_db("Boxes")
            delete_db("Images")
            conn.commit()
            cursor.close()
            sys.exit()
    except IndexError:
        pass
    
    # Creates tables if needed
    get_tables()
    print(cursor.fetchall())
    create_Images("Images",[("scan_id","SERIAL",True),("area","FLOAT4",False),("flawed","INT",False)])
    create_Boxes()

    get_table("Boxes")
    print(cursor.fetchall())
    get_table("Images")
    print(cursor.fetchall())

    save_scan(0.2,1)
    get_table("Images")
    print(cursor.fetchall())

    save_box(1,"scrach",0,0,150,150)
    get_table("Boxes")
    print(cursor.fetchall())


    print(get_data_for_heatmap("asdf"))
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
        result = cursor.execute(query)
    return wrapper

@execute
def get_table(table_name:str,*args):
    if not args:
        return f"SELECT * FROM {table_name}"
    
    query = f"SELECT * FROM {table_name} WHERE "
    for arg in args:
        query += f"{arg[0]} = '{arg[1]}' AND"

    return query.strip(" AND")

@execute
def create_Images(name:str,args:list[tuple[str]]):
    query =  f"""CREATE TABLE IF NOT EXISTS {name} ("""
    for item in args:
        if item[2]:
            query += f"\n{item[0]} {item[1]} PRIMARY KEY,"
        else:
            query += f"\n{item[0]} {item[1]} NOT NULL,"

    return query.strip(",") + ")"

@execute
def create_Boxes():
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
def clear_db(table_name:str):
    return f"""DELETE FROM {table_name}"""

@execute
def delete_db(table_name:str):
    return f"""DROP TABLE IF EXISTS {table_name}"""

@execute
def get_tables():
    return """SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"""

@execute
def save_scan(area:float,trash:bool):
    return f"INSERT INTO Images (area, flawed) VALUES ({area}, {trash});"

@execute
def save_box(scan_id:int, class_type:str, x_min:int, y_min:int, x_max:int, y_max:int):
    return f"INSERT INTO Boxes (scan_id, class_type, x_min, y_min, x_max, y_max) VALUES ({scan_id}, '{class_type}', {x_min}, {y_min}, {x_max}, {y_max});"

def get_data_for_heatmap(class_type:str|None = None):
    if class_type:
        get_table("Boxes",("class_type",class_type))
    else:
        get_table("Boxes")

    boxes = cursor.fetchall()

    return boxes
    
"{'scrach': [[0, 0, 100, 100], [1, 3, 4, 5]], 'asdf': [[50, 50, 150, 1500]]}"

if __name__=="__main__":
    main()