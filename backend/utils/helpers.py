from flask import jsonify

def success_response(data=None, status_code=200):
    response = {"success": True}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(code, message, status_code=400):
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }
    return jsonify(response), status_code

def format_api_response(success=True, data=None, error=None):
    resp = {"success": success}
    if data is not None:
        resp["data"] = data
    if error is not None:
        resp["error"] = error
    return resp

def paginate_query(query, request, default_per_page=20):
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', default_per_page))
    except (ValueError, TypeError):
        page = 1
        per_page = default_per_page
        
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [item.to_dict() if hasattr(item, 'to_dict') else item for item in pagination.items]
    
    return {
        "items": items,
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }
