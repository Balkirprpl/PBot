import mysql.connector


def batch_execute_ddl(conn, ddl_file_path):  # connection
    cursor = conn.cursor()
    ddl_file = open(ddl_file_path)
    sql = ddl_file.read()
    
    for result in cursor.execute(sql, multi=True):  # remove multi if you're executing 1 statement
        if result.with_rows:
            print(f"Rows returned: {result.statement}")
            print(result.fetchall())
        else:
            print(f"Number of rows affected by statement {result.statement}: {result.rowcount}")
    ddl_file.close()


##############################################################################################################################

def get_table_names(conn, ddl_file_path):  # connection
    cursor = conn.cursor()
    ddl_file = open(ddl_file_path)
    sql = ddl_file.read()
    table_query = []
    
    for result in cursor.execute(sql, multi=True):
        table_name = result.statement[13:22].replace("(", "").replace(" ", "")
        table_name = table_name.split("\n")
        if result.statement[0:12].replace("(", "").replace(" ", "") == "createtable":
            table_query.append(table_name[0])
    
    ddl_file.close()
    cursor.close()
    return table_query


def insert_CSV_data(table_name, conn):  # opens respective csv file and inserts data into correct table
    rows_affected_count = 0  # counts number of inserted rows
    csv_file_path = "database.csv"  # filepath to respective csv file
    csv_file = open(csv_file_path)
    
    sql_query = build_sql_query(table_name, csv_file)  # builds INSERT query for each table
    rows = build_row(csv_file)  # creates each table row as a list
    csv_file.close()
    
    print(sql_query)
    
    cursor = conn.cursor()
    for i in range(len(rows)):
        tuple_attributes = []
        for j in range(len(rows[i])):
            tuple_attributes.append(rows[i][j].replace("\n", ""))  # stores data to be inserted in single list
        
        record = tuple(tuple_attributes)  # list is converted into a tuple before insertion
        try:
            cursor.execute(sql_query,
                           record)  # the execute method will fill in each record value into the sql_query string
        except mysql.connector.Error as error:
            print("Warning:")
            print(error)
            print("When adding data", end='\n\n')
        rows_affected_count = rows_affected_count + cursor.rowcount  # increments after inserting record by the number of rows affected
        conn.commit()  # commit changes to the database
    
    print("number of rows affected for " + table_name + " table:",
          rows_affected_count)  # prints how many rows were inserted per table
    cursor.close()


def build_sql_query(table_name, csv_file):
    header = []  # stores headers in separate list
    header = next(csv_file).replace("\n", "")
    header = header.split(",")
    
    sql_query = """INSERT INTO """ + table_name + """("""
    for i in range(len(header)):
        if i != len(header) - 1:
            sql_query = sql_query + header[i] + """, """
        else:
            sql_query = sql_query + header[i]
    sql_query = sql_query + """) VALUES("""
    for i in range(len(header)):
        if i != len(header) - 1:
            sql_query = sql_query + """%s, """
        else:
            sql_query = sql_query + """%s"""
    sql_query = sql_query + """);"""  # dynamically creating the SQL query to insert csv data
    
    return sql_query


def build_row(csv_file):
    rows = []  # stores table data in separate lists
    for row in csv_file:
        row = row.split(",")
        rows.append(row)
    return rows


##############################################################################################################################

def main():
    host = 'localhost'
    user = 'root'
    password = open("credentials.txt").read()  # contains password
    conn = mysql.connector.connect(host=host,
                                   user=user,
                                   password=password)
    ddl_file_path = "bot_db.sql"
    
    batch_execute_ddl(conn, ddl_file_path)  # creates instance of .sql file
    
    table_names = get_table_names(conn, ddl_file_path)  # returns names of tables
    print(
        '########################################################################################################################')
    
    for table in table_names:  # inserts csv data into each table in database
        insert_CSV_data(table, conn)
    conn.close()
    print(
        '########################################################################################################################')


main()
