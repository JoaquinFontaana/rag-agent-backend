from langgraph_sdk import Auth
from src.security.jwt import verify_token

auth = Auth()

#Cant use without enterpise license
@auth.authenticate
async def authenticate(headers: dict):
    token = headers.get("bearrer-token")

    if not token:
        raise auth.exceptions.HTTPException(
            status_code=401,
            detail="No token provided"
        )
    
    payload = verify_token(token)

    return {
        "identity": payload.get("sub"),
        "is_authenticated": True,
        "role": payload.get("role")  # Include role for authorization
    }