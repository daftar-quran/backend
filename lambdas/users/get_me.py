from daftar_common.http_response import HttpResponse
from daftar_common.models.users import User
import jwt


def get_me(users_table, access_token):
    if not access_token:
        return HttpResponse.unauthorized(error="You must be logged in")
    
    decoded = jwt.decode(access_token[7:], options={"verify_signature": False})
    username = decoded.get('cognito:username')

    if not username:
        return HttpResponse.not_found(error="No username found in access token.")
 
    """
    try:
        username = cognito_identity_wrapper.get_username_by_access_token(access_token)
    except Exception as e:
        return HttpResponse.internal_error(error=f"Unknown Error : {e}")
    """
    # TODO: Replace scan by get_item
    all_users = users_table.scan_table()
    try:
        user = next(filter(lambda u: u.get('pseudo').lower() == username, all_users))
    except Exception:
        return HttpResponse.not_found(error="User not found.")

    user = User(**user)

    return HttpResponse.success(response_data=user.model_dump(mode='json'))
