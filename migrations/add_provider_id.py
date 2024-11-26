from app import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Ajouter la colonne provider_id
    op.add_column('appointment', sa.Column('provider_id', sa.Integer(), nullable=True))
    
    # Créer la contrainte de clé étrangère
    op.create_foreign_key(
        'fk_appointment_provider_id', 'appointment',
        'user', ['provider_id'], ['id']
    )
    
    # Mettre à jour les valeurs existantes
    connection = op.get_bind()
    connection.execute("""
        UPDATE appointment a
        JOIN provider_profile pp ON a.provider_profile_id = pp.id
        SET a.provider_id = pp.user_id
    """)
    
    # Rendre la colonne non nullable
    op.alter_column('appointment', 'provider_id',
                    existing_type=sa.Integer(),
                    nullable=False)

def downgrade():
    op.drop_constraint('fk_appointment_provider_id', 'appointment', type_='foreignkey')
    op.drop_column('appointment', 'provider_id')
