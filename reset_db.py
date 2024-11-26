from app import app, db
from sqlalchemy import text

def reset_database():
    with app.app_context():
        # Désactiver les contraintes de clé étrangère
        db.session.execute(text('SET FOREIGN_KEY_CHECKS=0'))
        
        # Supprimer les données de chaque table dans le bon ordre
        db.session.execute(text('TRUNCATE TABLE review'))
        db.session.execute(text('TRUNCATE TABLE appointment'))
        db.session.execute(text('TRUNCATE TABLE availability'))
        db.session.execute(text('TRUNCATE TABLE service'))
        db.session.execute(text('TRUNCATE TABLE provider_profile'))
        db.session.execute(text('TRUNCATE TABLE user'))
        
        # Réactiver les contraintes de clé étrangère
        db.session.execute(text('SET FOREIGN_KEY_CHECKS=1'))
        
        # Valider les changements
        db.session.commit()
        
        # Recréer les tables
        db.create_all()
        
        print("Base de données réinitialisée avec succès!")

if __name__ == '__main__':
    reset_database()
