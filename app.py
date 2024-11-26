from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, time
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, TimeField, BooleanField
from wtforms.fields import DateField, TimeField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus
from notifications import send_appointment_confirmation, send_appointment_cancelled, send_appointment_modified

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration de la base de données avec des paramètres de connexion optimisés
db_user = os.getenv('DATABASE_USER', 'u630971164_7d2Hg')
db_password = quote_plus(os.getenv('DATABASE_PASSWORD', 'EmineM81'))
db_host = os.getenv('DATABASE_HOST', 'srv1214.hstgr.io')
db_name = os.getenv('DATABASE_NAME', 'u630971164_OxvIs')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configuration de SQLAlchemy avec des paramètres de connexion optimisés
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{db_user}:{db_password}@{db_host}/{db_name}?charset=utf8mb4"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 280,
    'pool_pre_ping': True,
    'pool_timeout': 20,
    'connect_args': {
        'connect_timeout': 60,
        'read_timeout': 60,
        'write_timeout': 60
    }
}

# Configuration de Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@rdvous.com')

# Initialisation des extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(128))
    is_provider = db.Column(db.Boolean, default=False)
    appointments_as_client = db.relationship('Appointment', backref='client', foreign_keys='Appointment.client_id', lazy='dynamic')
    appointments_as_provider = db.relationship('Appointment', backref='provider', foreign_keys='Appointment.provider_id', lazy='dynamic')
    provider_profile = db.relationship('ProviderProfile', back_populates='user', uselist=False)
    reviews_given = db.relationship('Review', backref='client', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider_profile_id = db.Column(db.Integer, db.ForeignKey('provider_profile.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'client': self.client.name,
            'provider': self.provider_profile.user.name,
            'service': self.service.name,
            'date': self.date.isoformat(),
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'status': self.status
        }

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_profile_id = db.Column(db.Integer, db.ForeignKey('provider_profile.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Lundi, 6=Dimanche
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            'id': self.id,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time.strftime('%H:%M'),
            'end_time': self.end_time.strftime('%H:%M'),
            'is_available': self.is_available
        }

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer)  # durée en minutes
    price = db.Column(db.Float)
    provider_profile_id = db.Column(db.Integer, db.ForeignKey('provider_profile.id'), nullable=False)
    appointments = db.relationship('Appointment', backref='service', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'duration': self.duration,
            'price': self.price
        }

class ProviderProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    profession = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    specialties = db.Column(db.String(200))  # Liste de spécialités séparées par des virgules
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = db.relationship('User', back_populates='provider_profile')
    services = db.relationship('Service', backref='provider_profile', lazy=True)
    availabilities = db.relationship('Availability', backref='provider_profile', lazy=True)
    appointments = db.relationship('Appointment', backref='provider_profile', lazy=True)
    reviews = db.relationship('Review', backref='provider_profile', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider_profile_id = db.Column(db.Integer, db.ForeignKey('provider_profile.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'provider': self.provider_profile.user.name,
            'client': self.client.name,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat()
        }

def check_availability(provider_id, start_time, end_time, exclude_appointment_id=None):
    """
    Vérifie si un créneau horaire est disponible pour un prestataire
    """
    query = Appointment.query.filter(
        Appointment.provider_profile_id == provider_id,
        Appointment.status != 'cancelled',
        # Vérifie le chevauchement des horaires
        db.or_(
            # Cas 1: Le nouveau rendez-vous commence pendant un autre
            db.and_(
                start_time >= Appointment.start_time,
                start_time < Appointment.end_time
            ),
            # Cas 2: Le nouveau rendez-vous se termine pendant un autre
            db.and_(
                end_time > Appointment.start_time,
                end_time <= Appointment.end_time
            ),
            # Cas 3: Le nouveau rendez-vous englobe un autre
            db.and_(
                start_time <= Appointment.start_time,
                end_time >= Appointment.end_time
            )
        )
    )
    
    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)
    
    return query.first() is None

class AppointmentForm(FlaskForm):
    title = StringField('Titre du rendez-vous', validators=[
            DataRequired(message="Le titre est requis"),
            Length(min=3, max=100, message="Le titre doit contenir entre 3 et 100 caractères")
        ])
    description = TextAreaField('Description (optionnelle)', 
                                  validators=[Optional(), 
                                  Length(max=500, message="La description ne doit pas dépasser 500 caractères")])
    date = DateField('Date', 
                                 format='%Y-%m-%d',
                                 validators=[DataRequired(message="La date est requise")])
    start_time = TimeField('Heure de début', 
                                 validators=[DataRequired(message="L'heure est requise")])
    provider_id = SelectField('Prestataire', 
                                coerce=int,
                                validators=[DataRequired(message="Veuillez sélectionner un prestataire")])
    service_id = SelectField('Service', 
                                coerce=int,
                                validators=[DataRequired(message="Veuillez sélectionner un service")])

    def validate_start_time(self, field):
        if not self.service_id.data:
            return
            
        # Get the service duration
        service = Service.query.get(self.service_id.data)
        if not service:
            return
            
        # Calculate end time based on service duration
        start_datetime = datetime.combine(self.date.data, self.start_time.data)
        end_datetime = start_datetime + timedelta(minutes=service.duration)
        
        # Check if the appointment would end after business hours
        if end_datetime.time() > time(20, 0):  # 20:00
            raise ValidationError("Le rendez-vous ne peut pas se terminer après 20h")

class ContactForm(FlaskForm):
    name = StringField('Nom', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Sujet', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

class AvailabilityForm(FlaskForm):
    day_of_week = SelectField('Jour', coerce=int, choices=[
        (0, 'Lundi'), (1, 'Mardi'), (2, 'Mercredi'),
        (3, 'Jeudi'), (4, 'Vendredi'), (5, 'Samedi'), (6, 'Dimanche')
    ])
    start_time = TimeField('Heure de début', validators=[DataRequired()])
    end_time = TimeField('Heure de fin', validators=[DataRequired()])
    is_available = BooleanField('Disponible')

class BreakTimeForm(FlaskForm):
    start_datetime = DateTimeField('Date et heure de début', validators=[DataRequired()])
    end_datetime = DateTimeField('Date et heure de fin', validators=[DataRequired()])
    reason = StringField('Raison', validators=[DataRequired()])

class UserForm(FlaskForm):
    username = StringField('Nom d\'utilisateur', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Mot de passe')
    is_provider = BooleanField('Est un prestataire')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        is_provider = request.form.get('is_provider') == 'on'
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('register'))
        
        user = User(email=email, name=name, is_provider=is_provider)
        user.set_password(password)
        db.session.add(user)
        
        # Créer un profil prestataire si nécessaire
        if is_provider:
            profile = ProviderProfile(user_id=user.id)
            db.session.add(profile)
        
        db.session.commit()
        
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            
        flash('Email ou mot de passe incorrect.', 'danger')
    
    return render_template('login.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Ici vous pouvez ajouter la logique pour envoyer l'email
        # Par exemple, utiliser Flask-Mail
        flash('Votre message a été envoyé avec succès !', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/appointments')
@login_required
def appointments():
    user_appointments = current_user.appointments_as_client.all()
    provider_appointments = current_user.appointments_as_provider.all()
    return render_template('appointments.html', 
                         user_appointments=user_appointments,
                         provider_appointments=provider_appointments)

@app.route('/appointment/new', methods=['GET', 'POST'])
@login_required
def new_appointment():
    form = AppointmentForm()
    
    # Initialize provider choices
    providers = User.query.filter_by(is_provider=True).join(ProviderProfile).all()
    form.provider_id.choices = [(p.id, p.name) for p in providers]
    
    # Initialize service choices (empty by default, will be populated by AJAX)
    form.service_id.choices = []
    
    # If provider_id is in request args, pre-select it and load its services
    provider_id = request.args.get('provider_id', type=int)
    if provider_id:
        form.provider_id.data = provider_id
        provider = User.query.get_or_404(provider_id)
        if provider.provider_profile:
            form.service_id.choices = [(s.id, f"{s.name} ({s.duration} min - {s.price}€)") for s in provider.provider_profile.services]
    
    # Handle AJAX request for updating services
    if request.args.get('update_services'):
        provider_id = request.args.get('provider_id', type=int)
        if provider_id:
            provider = User.query.get_or_404(provider_id)
            if provider.provider_profile:
                services = provider.provider_profile.services
                return jsonify([(s.id, f"{s.name} ({s.duration} min - {s.price}€)") for s in services])
        return jsonify([])
    
    if form.validate_on_submit():
        provider = User.query.get_or_404(form.provider_id.data)
        if not provider.provider_profile:
            flash('Le profil du prestataire n\'existe pas.', 'danger')
            return redirect(url_for('appointments'))
            
        try:
            appointment = Appointment(
                provider_id=provider.id,
                provider_profile_id=provider.provider_profile.id,
                client_id=current_user.id,
                service_id=form.service_id.data,
                date=form.date.data,
                start_time=form.start_time.data,
                end_time=(datetime.combine(form.date.data, form.start_time.data) + timedelta(minutes=Service.query.get(form.service_id.data).duration)).time(),
                status='pending',
                title=form.title.data,
                description=form.description.data
            )
            db.session.add(appointment)
            db.session.commit()
            
            # Envoyer les notifications
            send_appointment_confirmation(appointment)
            
            flash('Votre demande de rendez-vous a été envoyée avec succès!', 'success')
            return redirect(url_for('appointments'))
            
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la création du rendez-vous. Veuillez réessayer.', 'danger')
            app.logger.error(f'Erreur lors de la création du rendez-vous: {str(e)}')
    
    return render_template('appointment_form.html', form=form, title='Nouveau Rendez-vous')

@app.route('/appointment/<int:id>')
@login_required
def view_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if appointment.client_id != current_user.id and appointment.provider_profile.user_id != current_user.id:
        flash('Vous n\'avez pas accès à ce rendez-vous.', 'danger')
        return redirect(url_for('appointments'))
    return render_template('appointment_detail.html', appointment=appointment)

@app.route('/appointment/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    if current_user.id != appointment.client_id and current_user.id != appointment.provider_profile.user_id:
        flash('Vous n\'êtes pas autorisé à modifier ce rendez-vous.', 'danger')
        return redirect(url_for('appointments'))
    
    form = AppointmentForm(obj=appointment)
    providers = User.query.filter_by(is_provider=True).order_by(User.name).all()
    form.provider_id.choices = [(p.id, p.name) for p in providers]
    
    if form.validate_on_submit():
        try:
            # Vérifier la disponibilité en excluant le rendez-vous actuel
            if check_availability(form.provider_id.data, form.start_time.data, (datetime.combine(form.date.data, form.start_time.data) + timedelta(minutes=Service.query.get(form.service_id.data).duration)).time(), exclude_appointment_id=id):
                appointment.provider_profile_id = form.provider_id.data
                appointment.date = form.date.data
                appointment.start_time = form.start_time.data
                appointment.end_time = (datetime.combine(form.date.data, form.start_time.data) + timedelta(minutes=Service.query.get(form.service_id.data).duration)).time()
                
                db.session.commit()
                
                # Envoyer les notifications de modification
                send_appointment_modified(appointment)
                
                flash('Rendez-vous mis à jour avec succès!', 'success')
                return redirect(url_for('appointments'))
            else:
                flash('Ce créneau horaire n\'est pas disponible pour ce prestataire', 'danger')
                
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la mise à jour du rendez-vous. Veuillez réessayer.', 'danger')
            app.logger.error(f'Erreur lors de la mise à jour du rendez-vous: {str(e)}')
    
    return render_template('appointment_form.html', form=form, title='Modifier le Rendez-vous')

@app.route('/appointment/<int:id>/status', methods=['POST'])
@login_required
def update_appointment_status(id):
    appointment = Appointment.query.get_or_404(id)
    if appointment.provider_profile.user_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    new_status = request.json.get('status')
    if new_status not in ['pending', 'confirmed', 'cancelled', 'completed']:
        return jsonify({'error': 'Statut invalide'}), 400
    
    old_status = appointment.status
    appointment.status = new_status
    db.session.commit()
    
    # Envoyer les notifications en cas d'annulation
    if new_status == 'cancelled' and old_status != 'cancelled':
        send_appointment_cancelled(appointment, current_user)
    
    return jsonify(appointment.to_dict())

@app.route('/availability/new', methods=['GET', 'POST'])
@login_required
def new_availability():
    form = AvailabilityForm()
    if form.validate_on_submit():
        availability = Availability(
            provider_profile_id=current_user.provider_profile.id,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            is_available=form.is_available.data
        )
        db.session.add(availability)
        db.session.commit()
        
        flash('Disponibilité créée avec succès!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('availability_form.html', form=form, title='Nouvelle Disponibilité')

@app.route('/break-time/new', methods=['GET', 'POST'])
@login_required
def new_break_time():
    form = BreakTimeForm()
    if form.validate_on_submit():
        break_time = BreakTime(
            provider_profile_id=current_user.provider_profile.id,
            start_datetime=form.start_datetime.data,
            end_datetime=form.end_datetime.data,
            reason=form.reason.data
        )
        db.session.add(break_time)
        db.session.commit()
        
        flash('Période de pause créée avec succès!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('break_time_form.html', form=form, title='Nouvelle Période de Pause')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/api/provider-availability/<int:provider_id>')
def get_provider_availability(provider_id):
    # Récupérer tous les rendez-vous non annulés du prestataire
    appointments = Appointment.query.filter(
        Appointment.provider_profile_id == provider_id,
        Appointment.status != 'cancelled'
    ).all()
    
    # Formater les rendez-vous pour le calendrier
    busy_slots = [{
        'start': appt.start_time.isoformat(),
        'end': appt.end_time.isoformat(),
        'title': 'Non disponible'
    } for appt in appointments]
    
    return jsonify(busy_slots)

@app.route('/api/provider-availability-calendar/<int:provider_id>')
def get_provider_availability_calendar(provider_id):
    # Récupérer la date de début (premier jour du mois en cours)
    today = datetime.now()
    start_date = today.replace(day=1)
    # Fin du mois suivant
    if today.month == 12:
        end_date = today.replace(year=today.year + 1, month=1, day=31)
    else:
        end_date = today.replace(month=today.month + 1, day=31)

    # Récupérer tous les rendez-vous du prestataire pour cette période
    appointments = Appointment.query.filter_by(provider_profile_id=provider_id)\
        .filter(Appointment.date >= start_date)\
        .filter(Appointment.date <= end_date)\
        .all()

    # Créer un dictionnaire pour stocker les disponibilités
    availability = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        availability[date_str] = {
            'morning': 'available',  # 8h-13h
            'afternoon': 'available' # 13h-20h
        }
        current_date += timedelta(days=1)

    # Marquer les créneaux occupés
    for appointment in appointments:
        date_str = appointment.date.strftime('%Y-%m-%d')
        start_hour = appointment.start_time.hour
        end_hour = appointment.end_time.hour
        
        # Si le rendez-vous est le matin (8h-13h)
        if start_hour < 13:
            availability[date_str]['morning'] = 'busy'
        
        # Si le rendez-vous est l'après-midi (13h-20h)
        if start_hour >= 13 or end_hour > 13:
            availability[date_str]['afternoon'] = 'busy'
        
        # Si le rendez-vous s'étend sur toute la journée
        if start_hour < 13 and end_hour > 13:
            availability[date_str]['morning'] = 'busy'
            availability[date_str]['afternoon'] = 'busy'

    # Marquer les dates passées comme indisponibles
    for date_str in availability:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        if date.date() < today.date():
            availability[date_str]['morning'] = 'past'
            availability[date_str]['afternoon'] = 'past'
        elif date.date() == today.date():
            if today.hour >= 13:
                availability[date_str]['morning'] = 'past'
            if today.hour >= 20:
                availability[date_str]['afternoon'] = 'past'

    return jsonify(availability)

@app.route('/providers')
def list_providers():
    profession = request.args.get('profession')
    
    query = User.query.filter_by(is_provider=True).join(User.provider_profile)
    
    if profession:
        query = query.filter(
            ProviderProfile.profession.like(f'%{profession}%')
        )
    
    providers = query.all()
    return render_template('providers/list.html', providers=providers)

@app.route('/provider/<int:provider_id>')
def provider_profile(provider_id):
    provider = User.query.get_or_404(provider_id)
    if not provider.is_provider:
        abort(404)
        
    profile = provider.provider_profile
    if not profile:
        abort(404)
        
    services = profile.services
    reviews = Review.query.filter_by(provider_profile_id=profile.id)\
        .order_by(Review.created_at.desc())\
        .limit(5)\
        .all()
    
    # Calculate average rating
    all_reviews = Review.query.filter_by(provider_profile_id=profile.id).all()
    average_rating = 0
    if all_reviews:
        total_rating = sum(review.rating for review in all_reviews)
        average_rating = total_rating / len(all_reviews)
        
    return render_template('providers/profile.html',
                         provider=provider,
                         profile=profile,
                         services=services,
                         reviews=reviews,
                         average_rating=average_rating)

@app.route('/provider/profile', methods=['GET', 'POST'])
@login_required
def edit_provider_profile():
    if not current_user.is_provider:
        abort(403)
        
    profile = current_user.provider_profile or ProviderProfile(user_id=current_user.id)
    
    if request.method == 'POST':
        profile.profession = request.form.get('profession')
        profile.description = request.form.get('description')
        profile.specialties = request.form.get('specialties')
        profile.experience_years = request.form.get('experience_years')
        profile.education = request.form.get('education')
        profile.languages = request.form.get('languages')
        profile.location = request.form.get('location')
        profile.consultation_address = request.form.get('consultation_address')
        profile.phone = request.form.get('phone')
        profile.website = request.form.get('website')
        
        # Gestion de l'upload de photo
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile.profile_picture = filename
        
        db.session.add(profile)
        db.session.commit()
        flash('Profil mis à jour avec succès!', 'success')
        return redirect(url_for('provider_profile', provider_id=current_user.id))
        
    return render_template('providers/edit_profile.html', profile=profile)

@app.route('/provider/<int:provider_id>/services', methods=['GET', 'POST'])
@login_required
def manage_services(provider_id):
    if current_user.id != provider_id or not current_user.is_provider:
        abort(403)
        
    if request.method == 'POST':
        service = Service(
            name=request.form.get('name'),
            description=request.form.get('description'),
            duration=request.form.get('duration'),
            price=request.form.get('price'),
            provider_profile_id=provider_id
        )
        db.session.add(service)
        db.session.commit()
        flash('Service ajouté avec succès!', 'success')
        return redirect(url_for('manage_services', provider_id=provider_id))
        
    services = Service.query.filter_by(provider_profile_id=provider_id).all()
    return render_template('providers/manage_services.html', services=services)

@app.route('/review/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def add_review(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if current_user.id != appointment.client_id:
        abort(403)
        
    if request.method == 'POST':
        review = Review(
            provider_profile_id=appointment.provider_profile_id,
            client_id=current_user.id,
            rating=request.form.get('rating'),
            comment=request.form.get('comment')
        )
        db.session.add(review)
        
        # Mettre à jour la moyenne des notes du prestataire
        provider = User.query.get(appointment.provider_profile.user_id)
        total_rating = provider.average_rating * provider.total_reviews
        provider.total_reviews += 1
        provider.average_rating = (total_rating + int(request.form.get('rating'))) / provider.total_reviews
        
        db.session.commit()
        flash('Merci pour votre avis!', 'success')
        return redirect(url_for('appointment_details', id=appointment_id))
        
    return render_template('review_form.html', appointment=appointment)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
