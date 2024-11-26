from app import app, db, User, ProviderProfile, Service
from werkzeug.security import generate_password_hash

def add_test_providers():
    with app.app_context():
        # Check if users already exist
        existing_doctor = User.query.filter_by(email='docteur@example.com').first()
        existing_consultant = User.query.filter_by(email='consultant@example.com').first()

        if existing_doctor:
            print("Doctor already exists, skipping...")
            doctor = existing_doctor
        else:
            # Création du médecin
            doctor = User(
                email='docteur@example.com',
                name='Dr. Martin',
                password_hash=generate_password_hash('password123'),
                is_provider=True
            )
            db.session.add(doctor)
            db.session.flush()  # Pour obtenir l'ID du docteur

            doctor_profile = ProviderProfile(
                user_id=doctor.id,
                profession='Médecin Généraliste',
                description='Médecin généraliste expérimenté avec plus de 10 ans de pratique.',
                address='123 Avenue de la Santé, Paris',
                phone='01 23 45 67 89'
            )
            db.session.add(doctor_profile)
            db.session.flush()  # Flush to get the doctor_profile ID

            # Services du médecin
            consultation_med = Service(
                name='Consultation médicale',
                description='Consultation médicale générale',
                duration=30,
                price=25.00,
                provider_profile_id=doctor_profile.id
            )
            db.session.add(consultation_med)

        if existing_consultant:
            print("Consultant already exists, skipping...")
            consultant = existing_consultant
        else:
            # Création du consultant
            consultant = User(
                email='consultant@example.com',
                name='Sophie Dubois',
                password_hash=generate_password_hash('password123'),
                is_provider=True
            )
            db.session.add(consultant)
            db.session.flush()  # Pour obtenir l'ID du consultant

            consultant_profile = ProviderProfile(
                user_id=consultant.id,
                profession='Consultant Business',
                description='Consultante en stratégie d\'entreprise et développement commercial.',
                address='456 Rue des Affaires, Paris',
                phone='01 98 76 54 32'
            )
            db.session.add(consultant_profile)
            db.session.flush()  # Flush to get the consultant_profile ID

            # Services du consultant
            consultation_business = Service(
                name='Consultation stratégique',
                description='Analyse et conseils en stratégie d\'entreprise',
                duration=60,
                price=150.00,
                provider_profile_id=consultant_profile.id
            )
            db.session.add(consultation_business)

        # Commit des changements
        db.session.commit()

        print("Opération terminée avec succès!")
        print("Médecin - Email: docteur@example.com, Mot de passe: password123")
        print("Consultant - Email: consultant@example.com, Mot de passe: password123")

if __name__ == '__main__':
    add_test_providers()
