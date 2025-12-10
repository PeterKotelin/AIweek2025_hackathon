import psycopg2

def main():
        try:
            conn = psycopg2.connect(
                dbname="your_database_name",
                user="your_username",
                password="your_password",
                host="your_host",
                port=5432
            )
            print("Connected to PostgreSQL successfully!")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
        
            cursor = conn.cursor()

        print("shit")
        # Example: Creating a table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        );
        """
        cursor.execute(create_table_query)
        conn.commit() # Commit the changes to the database
        print("Table 'users' created successfully.")

        # Example: Inserting data
        insert_data_query = "INSERT INTO users (name, email) VALUES (%s, %s);"
        cursor.execute(insert_data_query, ("Alice", "alice@example.com"))
        conn.commit()
        print("Data inserted successfully.")

        # Example: Retrieving data
        select_data_query = "SELECT * FROM users;"
        cursor.execute(select_data_query)
        rows = cursor.fetchall()
        for row in rows:
            print(row)


if __name__=="__main__":
    main()