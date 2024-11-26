import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, app

def add_column_if_not_exists(conn, table, column, definition):
    try:
        conn.execute(db.text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
        print(f"Successfully added column {column}")
    except Exception as e:
        if "Duplicate column name" in str(e):
            print(f"Column {column} already exists")
        else:
            raise e

def upgrade():
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                # Add each column individually
                add_column_if_not_exists(conn, "appointment", "date", "DATE NOT NULL")
                add_column_if_not_exists(conn, "appointment", "start_time", "TIME NOT NULL")
                add_column_if_not_exists(conn, "appointment", "end_time", "TIME NOT NULL")
                add_column_if_not_exists(conn, "appointment", "status", "VARCHAR(20) DEFAULT 'pending'")
                add_column_if_not_exists(conn, "appointment", "notes", "TEXT")
                add_column_if_not_exists(conn, "appointment", "created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP")
                add_column_if_not_exists(conn, "appointment", "updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
                add_column_if_not_exists(conn, "appointment", "title", "VARCHAR(100) NOT NULL")
                add_column_if_not_exists(conn, "appointment", "description", "TEXT")
                
                print("Finished adding columns to appointment table")
    except Exception as e:
        print(f"Error adding columns: {str(e)}")
        raise e

def downgrade():
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                # Remove columns in reverse order
                columns = ["description", "title", "updated_at", "created_at", "notes", 
                          "status", "end_time", "start_time", "date"]
                for column in columns:
                    try:
                        conn.execute(db.text(f"ALTER TABLE appointment DROP COLUMN {column}"))
                        print(f"Successfully removed column {column}")
                    except Exception as e:
                        print(f"Error removing column {column}: {str(e)}")
                
                print("Finished removing columns from appointment table")
    except Exception as e:
        print(f"Error removing columns: {str(e)}")
        raise e

if __name__ == '__main__':
    upgrade()
