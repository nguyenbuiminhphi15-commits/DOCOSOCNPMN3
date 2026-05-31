import pyodbc

def dump_database():
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=Hutech_SecureQR;Trusted_Connection=yes;')
    cursor = conn.cursor()

    cursor.execute("""
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_CATALOG='Hutech_SecureQR'
    """)
    tables = [row[0] for row in cursor.fetchall()]

    with open('Hutech_SecureQR.sql', 'w', encoding='utf-8') as f:
        f.write('USE [Hutech_SecureQR]\nGO\n\n')
        for table in tables:
            cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{table}'
            ORDER BY ORDINAL_POSITION
            """)
            columns = cursor.fetchall()
            
            f.write(f'CREATE TABLE [{table}] (\n')
            col_defs = []
            for col in columns:
                name = col[0]
                dtype = col[1]
                length = col[2]
                nullable = 'NULL' if col[3] == 'YES' else 'NOT NULL'
                if dtype in ['varchar', 'nvarchar', 'char', 'nchar']:
                    dtype_str = f'{dtype}(MAX)' if length == -1 else f'{dtype}({length})'
                else:
                    dtype_str = dtype
                col_defs.append(f'    [{name}] {dtype_str} {nullable}')
            
            f.write(',\n'.join(col_defs))
            f.write('\n);\nGO\n\n')

            # Dump data
            try:
                cursor.execute(f'SELECT * FROM [{table}]')
                rows = cursor.fetchall()
                for row in rows:
                    vals = []
                    for val in row:
                        if val is None:
                            vals.append('NULL')
                        elif isinstance(val, str):
                            vals.append(f"N'{val.replace(chr(39), chr(39)+chr(39))}'")
                        elif isinstance(val, bool):
                            vals.append('1' if val else '0')
                        else:
                            vals.append(f"'{str(val)}'")
                    f.write(f"INSERT INTO [{table}] VALUES ({','.join(vals)});\n")
                f.write('GO\n\n')
            except Exception as e:
                f.write(f'-- Error dumping data for {table}: {str(e)}\n')

if __name__ == '__main__':
    dump_database()
    print('Done!')
