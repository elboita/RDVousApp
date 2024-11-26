import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, app, Appointment, User, Service

def update_appointments():
    try:
        with app.app_context():
            # Get all appointments
            appointments = Appointment.query.all()
            
            # Get a default service to use if none exists
            default_service = Service.query.first()
            if not default_service:
                # Create a default service if none exists
                default_service = Service(
                    name="Consultation standard",
                    description="Consultation standard de 30 minutes",
                    duration=30,
                    price=50.0,
                    provider_profile_id=1  # Make sure this ID exists
                )
                db.session.add(default_service)
                db.session.commit()
            
            for appointment in appointments:
                # Get the provider's profile ID
                provider = User.query.get(appointment.provider_id)
                if provider and provider.provider_profile:
                    appointment.provider_profile_id = provider.provider_profile.id
                    
                    # Try to find a service for this provider
                    service = Service.query.filter_by(provider_profile_id=provider.provider_profile.id).first()
                    if service:
                        appointment.service_id = service.id
                    else:
                        # Use default service if no provider-specific service exists
                        appointment.service_id = default_service.id
            
            # Commit all changes
            db.session.commit()
            print("Successfully updated provider_profile_id and service_id for all appointments")
            
    except Exception as e:
        print(f"Error updating appointments: {str(e)}")
        db.session.rollback()
        raise e

if __name__ == '__main__':
    update_appointments()
