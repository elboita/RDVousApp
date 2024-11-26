import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def upgrade():
    # Add provider_profile_id column to the review table
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE review ADD COLUMN provider_profile_id INT NOT NULL'))
                conn.execute(text('ALTER TABLE review ADD FOREIGN KEY (provider_profile_id) REFERENCES provider_profile(id)'))
                conn.commit()
            print("Column 'provider_profile_id' added successfully to the review table")
        except Exception as e:
            print(f"Error adding column 'provider_profile_id': {str(e)}")

def downgrade():
    # Remove provider_profile_id column from the review table
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE review DROP FOREIGN KEY review_ibfk_2'))  # Drop the foreign key first
                conn.execute(text('ALTER TABLE review DROP COLUMN provider_profile_id'))
                conn.commit()
            print("Column 'provider_profile_id' removed from the review table")
        except Exception as e:
            print(f"Error removing column 'provider_profile_id': {str(e)}")

if __name__ == '__main__':
    upgrade()
