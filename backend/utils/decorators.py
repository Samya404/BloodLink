from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models.user import User
from utils.helpers import error_response

def roles_required(*roles):
    # Normalize roles to uppercase
    normalized_roles = [r.upper() for r in roles]
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role.upper() not in normalized_roles:
                return error_response("UNAUTHORIZED", "You do not have access to this resource.", 403)
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# Alias for singular role_required
def role_required(*roles):
    return roles_required(*roles)

def admin_required(fn):
    return roles_required('ADMIN')(fn)
