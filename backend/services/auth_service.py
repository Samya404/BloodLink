from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from extensions import db
from models.user import User
from models.donor import DonorProfile
from models.hospital import Hospital

class AuthService:
    @staticmethod
    def register_user(data):
        """Create user, hash password, return user."""
        try:
            hashed_pw = generate_password_hash(data['password'])
            user = User(
                full_name=data['full_name'],
                email=data['email'],
                password_hash=hashed_pw,
                phone=data.get('phone'),
                role=data['role']
            )
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise ValueError("Registration failed: Email may already be in use.")

    @staticmethod  
    def login_user(email, password):
        """Verify credentials, return access_token, refresh_token"""
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid email or password.")
            
        if not getattr(user, 'is_active', True):
            raise ValueError("Account is inactive.")
            
        access_token = create_access_token(identity={'id': user.id, 'role': user.role})
        refresh_token = create_refresh_token(identity={'id': user.id, 'role': user.role})
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user
        }

    @staticmethod
    def get_user_by_id(user_id):
        """Return user dict or object"""
        return User.query.get(user_id)

    @staticmethod
    def create_donor_profile(user_id, data):
        """Create donor profile after registration"""
        profile = DonorProfile(user_id=user_id, **data)
        db.session.add(profile)
        db.session.commit()
        return profile

    @staticmethod
    def create_hospital(user_id, data):
        """Create hospital record after registration"""
        hospital = Hospital(user_id=user_id, **data)
        db.session.add(hospital)
        db.session.commit()
        return hospital
