import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, app

def upgrade():
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE appointment 
                    ADD COLUMN provider_profile_id INT NOT NULL,
                    ADD CONSTRAINT fk_appointment_provider_profile 
                    FOREIGN KEY (provider_profile_id) 
                    REFERENCES provider_profile(id)
                """))
                print("Successfully added provider_profile_id column to appointment table")
    except Exception as e:
        print(f"Error adding column: {str(e)}")
        raise e

def downgrade():
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE appointment 
                    DROP FOREIGN KEY fk_appointment_provider_profile,
                    DROP COLUMN provider_profile_id
                """))
                print("Successfully removed provider_profile_id column from appointment table")
    except Exception as e:
        print(f"Error removing column: {str(e)}")
        raise e

if __name__ == '__main__':
    upgrade()
