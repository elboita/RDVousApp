import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def upgrade():
    with app.app_context():
        # Ajouter la colonne is_provider
        with db.engine.connect() as connection:
            connection.execute(text('ALTER TABLE user ADD COLUMN is_provider BOOLEAN DEFAULT FALSE'))
            connection.commit()

def downgrade():
    with app.app_context():
        # Supprimer la colonne is_provider
        with db.engine.connect() as connection:
            connection.execute(text('ALTER TABLE user DROP COLUMN is_provider'))
            connection.commit()

def main():
    with app.app_context():
        # Ajouter la colonne is_provider
        with db.engine.connect() as connection:
            connection.execute(text('ALTER TABLE user ADD COLUMN is_provider BOOLEAN DEFAULT FALSE'))
            connection.commit()
        print("Migration completed successfully")

if __name__ == '__main__':
    main()
