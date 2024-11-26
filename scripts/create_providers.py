import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User

def create_providers():
    with app.app_context():
        # Créer un médecin
        doctor = User(
            username='Dr.Martin',
            email='dr.martin@example.com',
            is_provider=True
        )
        doctor.set_password('password123')

        # Créer un consultant
        consultant = User(
            username='ConsultantDupont',
            email='consultant.dupont@example.com',
            is_provider=True
        )
        consultant.set_password('password123')

        # Ajouter les utilisateurs à la base de données
        db.session.add(doctor)
        db.session.add(consultant)
        
        try:
            db.session.commit()
            print("Prestataires créés avec succès!")
            print("Médecin - Email: dr.martin@example.com, Mot de passe: password123")
            print("Consultant - Email: consultant.dupont@example.com, Mot de passe: password123")
        except Exception as e:
            print(f"Erreur lors de la création des prestataires: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_providers()
