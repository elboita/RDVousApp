from app import db, app
import sys

def init_db():
    try:
        with app.app_context():
            # Demander confirmation
            confirm = input("Attention: Ceci va effacer toutes les données existantes. Continuer? (y/N): ")
            if confirm.lower() != 'y':
                print("Opération annulée.")
                return

            # Initialiser la base de données
            db.drop_all()
            db.create_all()
            print("Base de données initialisée avec succès!")
    except Exception as e:
        print(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    init_db()
