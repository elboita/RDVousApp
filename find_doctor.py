from app import app, User

with app.app_context():
    doctor = User.query.filter_by(email='docteur@example.com').first()
    if doctor:
        print(f"ID du Dr. Martin: {doctor.id}")
        print(f"Lien du profil: http://localhost:5000/provider_profile/{doctor.id}")
    else:
        print("Docteur non trouvé")
