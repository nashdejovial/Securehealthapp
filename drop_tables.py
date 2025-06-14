import psycopg2
from config import Config

def drop_all_tables():
    # Connect to the database
    conn = psycopg2.connect(
        dbname="health_system",
        user="postgres",
        password="shifu",
        host="localhost",
        port="5432"
    )
    
    # Create a cursor
    cur = conn.cursor()
    
    try:
        # Drop all tables with CASCADE
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        
        # Commit the changes
        conn.commit()
        print("All tables dropped successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()

if __name__ == "__main__":
    drop_all_tables() 