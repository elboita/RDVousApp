import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def upgrade():
    # Add title and description columns to the appointment table
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE appointment ADD COLUMN title VARCHAR(100) NOT NULL DEFAULT "Rendez-vous"'))
                conn.execute(text('ALTER TABLE appointment ADD COLUMN description TEXT'))
                conn.commit()
            print("Columns 'title' and 'description' added successfully to the appointment table")
        except Exception as e:
            print(f"Error adding columns 'title' and 'description': {str(e)}")

def downgrade():
    # Remove title and description columns from the appointment table
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE appointment DROP COLUMN description'))
                conn.execute(text('ALTER TABLE appointment DROP COLUMN title'))
                conn.commit()
            print("Columns 'title' and 'description' removed from the appointment table")
        except Exception as e:
            print(f"Error removing columns 'title' and 'description': {str(e)}")

if __name__ == '__main__':
    upgrade()
