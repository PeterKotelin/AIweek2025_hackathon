import log


def main():
    cursor = log.connect_to_bd()
    # log.cursor
    # log.conn

    log.get_table("Boxes",cursor = cursor)
    print(cursor.fetchall())

    log.get_table("Images",("date","2025-12-10"),cursor = cursor)
    print(cursor.fetchall())

if __name__=="__main__":
    main()