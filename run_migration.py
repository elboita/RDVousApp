from app import app, db
from migrations.add_is_provider import upgrade

if __name__ == '__main__':
    with app.app_context():
        print("Exécution de la migration pour ajouter la colonne is_provider...")
        upgrade()
        print("Migration terminée avec succès !")
