from flask_mail import Mail, Message
from flask import render_template
from threading import Thread
from datetime import datetime, timedelta

mail = Mail()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, template, **kwargs):
    """Envoie un email en utilisant un template HTML."""
    from app import app  # Import local pour éviter les imports circulaires
    
    msg = Message(subject,
                 sender=app.config['MAIL_DEFAULT_SENDER'],
                 recipients=recipients)
    
    msg.html = render_template(f'emails/{template}.html', **kwargs)
    
    # Envoi asynchrone de l'email
    Thread(target=send_async_email, args=(app, msg)).start()

def send_appointment_confirmation(appointment):
    """Envoie un email de confirmation au client et au prestataire."""
    # Email au client
    send_email(
        subject='Confirmation de votre rendez-vous',
        recipients=[appointment.client.email],
        template='appointment_confirmation_client',
        appointment=appointment
    )
    
    # Email au prestataire
    send_email(
        subject='Nouveau rendez-vous',
        recipients=[appointment.provider.email],
        template='appointment_confirmation_provider',
        appointment=appointment
    )

def send_appointment_reminder(appointment):
    """Envoie un rappel de rendez-vous."""
    send_email(
        subject='Rappel de rendez-vous',
        recipients=[appointment.client.email, appointment.provider.email],
        template='appointment_reminder',
        appointment=appointment
    )

def send_appointment_cancelled(appointment, cancelled_by):
    """Envoie une notification d'annulation."""
    # Email au client
    if cancelled_by != appointment.client:
        send_email(
            subject='Votre rendez-vous a été annulé',
            recipients=[appointment.client.email],
            template='appointment_cancelled_client',
            appointment=appointment
        )
    
    # Email au prestataire
    if cancelled_by != appointment.provider:
        send_email(
            subject='Rendez-vous annulé',
            recipients=[appointment.provider.email],
            template='appointment_cancelled_provider',
            appointment=appointment
        )

def send_appointment_modified(appointment, modified_by):
    """Envoie une notification de modification."""
    # Email au client
    if modified_by != appointment.client:
        send_email(
            subject='Votre rendez-vous a été modifié',
            recipients=[appointment.client.email],
            template='appointment_modified_client',
            appointment=appointment
        )
    
    # Email au prestataire
    if modified_by != appointment.provider:
        send_email(
            subject='Rendez-vous modifié',
            recipients=[appointment.provider.email],
            template='appointment_modified_provider',
            appointment=appointment
        )

def schedule_appointment_reminders():
    """Planifie l'envoi des rappels de rendez-vous."""
    from app import app, Appointment  # Import local pour éviter les imports circulaires
    
    with app.app_context():
        # Trouve les rendez-vous qui commencent dans 24h
        tomorrow = datetime.now() + timedelta(days=1)
        appointments = Appointment.query.filter(
            Appointment.start_time.between(
                tomorrow - timedelta(minutes=30),
                tomorrow + timedelta(minutes=30)
            ),
            Appointment.status == 'confirmed'
        ).all()
        
        for appointment in appointments:
            send_appointment_reminder(appointment)
