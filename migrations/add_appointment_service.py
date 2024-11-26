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
                    ADD COLUMN service_id INT NOT NULL,
                    ADD CONSTRAINT fk_appointment_service
                    FOREIGN KEY (service_id) 
                    REFERENCES service(id)
                """))
                print("Successfully added service_id column to appointment table")
    except Exception as e:
        print(f"Error adding column: {str(e)}")
        raise e

def downgrade():
    try:
        with app.app_context():
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    ALTER TABLE appointment 
                    DROP FOREIGN KEY fk_appointment_service,
                    DROP COLUMN service_id
                """))
                print("Successfully removed service_id column from appointment table")
    except Exception as e:
        print(f"Error removing column: {str(e)}")
        raise e

if __name__ == '__main__':
    upgrade()
