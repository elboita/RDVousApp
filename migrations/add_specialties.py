import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text

def upgrade():
    # Ajout de la colonne specialties à la table provider_profile
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE provider_profile ADD COLUMN specialties VARCHAR(200)'))
                conn.commit()
            print("Colonne 'specialties' ajoutée avec succès à la table provider_profile")
        except Exception as e:
            print(f"Erreur lors de l'ajout de la colonne 'specialties': {str(e)}")

def downgrade():
    # Suppression de la colonne specialties de la table provider_profile
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE provider_profile DROP COLUMN specialties'))
                conn.commit()
            print("Colonne 'specialties' supprimée de la table provider_profile")
        except Exception as e:
            print(f"Erreur lors de la suppression de la colonne 'specialties': {str(e)}")

if __name__ == '__main__':
    upgrade()
