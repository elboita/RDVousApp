from app import app, db
from app import User, ProviderProfile, Service

def create_test_users():
    with app.app_context():
        # Création du médecin
        doctor = User(
            name="Dr. Sarah Martin",
            email="dr.martin@example.com",
            is_provider=True
        )
        doctor.set_password("Test123!")
        db.session.add(doctor)
        db.session.flush()  # Pour obtenir l'ID du médecin

        # Profil du médecin
        doctor_profile = ProviderProfile(
            user_id=doctor.id,
            profession="Médecin généraliste",
            description="Médecin généraliste avec 10 ans d'expérience, spécialisée en médecine préventive et suivi des maladies chroniques.",
            address="15 rue de la Santé, 75013 Paris",
            phone="01 23 45 67 89"
        )
        db.session.add(doctor_profile)
        db.session.flush()  # Pour obtenir l'ID du profil

        # Services du médecin
        doctor_services = [
            Service(
                provider_profile_id=doctor_profile.id,
                name="Consultation générale",
                description="Consultation médicale standard de 20 minutes",
                duration=20,
                price=25.00
            ),
            Service(
                provider_profile_id=doctor_profile.id,
                name="Bilan de santé complet",
                description="Bilan de santé approfondi avec examens détaillés",
                duration=45,
                price=60.00
            )
        ]
        for service in doctor_services:
            db.session.add(service)

        # Création du consultant
        consultant = User(
            name="Marc Dubois",
            email="marc.dubois@example.com",
            is_provider=True
        )
        consultant.set_password("Test123!")
        db.session.add(consultant)
        db.session.flush()  # Pour obtenir l'ID du consultant

        # Profil du consultant
        consultant_profile = ProviderProfile(
            user_id=consultant.id,
            profession="Consultant en stratégie",
            description="Consultant en stratégie d'entreprise avec expertise en transformation digitale et gestion du changement.",
            address="25 avenue des Champs-Élysées, 75008 Paris",
            phone="01 98 76 54 32"
        )
        db.session.add(consultant_profile)
        db.session.flush()  # Pour obtenir l'ID du profil

        # Services du consultant
        consultant_services = [
            Service(
                provider_profile_id=consultant_profile.id,
                name="Consultation stratégique",
                description="Analyse stratégique et recommandations pour votre entreprise",
                duration=60,
                price=150.00
            ),
            Service(
                provider_profile_id=consultant_profile.id,
                name="Audit digital",
                description="Évaluation de votre présence digitale et recommandations",
                duration=120,
                price=300.00
            )
        ]
        for service in consultant_services:
            db.session.add(service)

        # Commit des changements
        db.session.commit()

        print("✅ Utilisateurs de test créés avec succès!")
        print("\nComptes créés:")
        print("1. Médecin:")
        print("   - Email: dr.martin@example.com")
        print("   - Mot de passe: Test123!")
        print("\n2. Consultant:")
        print("   - Email: marc.dubois@example.com")
        print("   - Mot de passe: Test123!")

if __name__ == '__main__':
    create_test_users()
