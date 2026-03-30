from pydantic import EmailStr
from shared_schemas import ResponseMessage, UuidSchema


##############################################################################################
# --- Minimal user for internal stuff ---
##############################################################################################
class ResponseAccessToken(ResponseMessage):
    token_type: str = "bearer"
    access_token: str


##############################################################################################
# --- Register ---
##############################################################################################
class ResponseRegister(ResponseMessage):
    message: str = "Registro correcto"
    username: str
    email: EmailStr


##############################################################################################
# --- Login ---
##############################################################################################
class ResponseLogin(ResponseAccessToken):
    message: str = "Login correcto"
    username: str


##############################################################################################
# --- Delete User ---
##############################################################################################
class ResponseDelete(ResponseMessage):
    message: str = "Registro correcto"
    username: str
    email: EmailStr


##############################################################################################
# --- Reauth ---
##############################################################################################
class ResponseReauth(ResponseAccessToken):
    message: str = "Reauth correcto"


##############################################################################################
# --- Logout ---
##############################################################################################
class ResponseLogout(ResponseMessage):
    message: str = "Logout correcto"


##############################################################################################
# --- Profile Update (can change email + username) ---
##############################################################################################
class ResponseUpdate(ResponseMessage):
    message: str = "Update correcto"


class CurrentUser(UuidSchema):
    pass
