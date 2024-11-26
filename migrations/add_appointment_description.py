import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def upgrade():
    # Add description column to the appointment table
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE appointment ADD COLUMN description TEXT'))
                conn.commit()
            print("Column 'description' added successfully to the appointment table")
        except Exception as e:
            print(f"Error adding column 'description': {str(e)}")

def downgrade():
    # Remove description column from the appointment table
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE appointment DROP COLUMN description'))
                conn.commit()
            print("Column 'description' removed from the appointment table")
        except Exception as e:
            print(f"Error removing column 'description': {str(e)}")

if __name__ == '__main__':
    upgrade()
