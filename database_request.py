import mysql.connector


def request_data_from_database():
    host = 'localhost'
    user = 'root'
    password = open("credentials.txt").read().strip()  # Strip newline characters
    database = 'bot_db'
    
    # Establish connection to the database
    conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor()
    
    try:
        # Execute the SQL query
        cursor.execute("SELECT * FROM user_info")
        
        # Fetch column names (headers)
        headers = [i[0] for i in cursor.description]
        
        # Print headers
        print(" | ".join(headers))
        print("-" * (len(" | ".join(headers))))
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Print the fetched data
        for row in rows:
            print(" | ".join(map(str, row)))
    
    except mysql.connector.Error as err:
        print("Error:", err)
    
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()


# Call the method to request data from the database
request_data_from_database()
