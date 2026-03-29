import os
import uuid
from pydantic import EmailStr, SecretStr
from fastapi import HTTPException, Response, status

from sqlalchemy.ext.asyncio import AsyncSession

from shared.auth.auth import CurrentUser
from shared.utils.auth import TokenService, hash_password, verify_password, HashError, HashMismatch, InvalidHashFormat
from shared.utils.text import TextUtils

from shared.ops.user import UsersDb
from shared.schemas.auth import ResponseRegister, ResponseLogin, ResponseReauth, ResponseLogout, ResponseDelete, ResponseUpdate

PRODUCTION_MODE = os.getenv("PRODUCTION_MODE", "False").lower() in ("1", "true", "yes")

class AuthHandler:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.userondb = UsersDb(self.db)
        self.textutils = TextUtils()



    async def register(self, username_api: str, email_api: EmailStr, password_api: SecretStr) -> ResponseRegister:
        username = self.textutils.sanitize_text(username_api)
        email = self.textutils.is_valid_and_safe_email(email_api)

        dup = await self.userondb.check_user_duplicity(username, email)
        if dup:
            raise HTTPException(status_code=400, detail="El usuario o email ya existe.")

        hashed_password = hash_password(password_api.get_secret_value())

        await self.userondb.create_user_entry(username, email, hashed_password)
    
        return ResponseRegister(
            username=username,
            email=email
        )

    async def UserDelete(self, username_api:str, email_api:EmailStr, password_api:SecretStr) -> ResponseDelete:
        username = self.textutils.sanitize_text(username_api)
        password = hash_password(password_api.get_secret_value())
        email = self.textutils.is_valid_and_safe_email(email_api)

        await self.userondb.delete_user_entry(username=username, email=email, passwd=password)
        return ResponseDelete(
            username=username,
            email=email
        )



    async def UserUpdateUsername(self, current_user: CurrentUser, username_api:str) -> ResponseUpdate:
        username = self.textutils.sanitize_text(username_api)

        await self.userondb.update_user_entry(id=current_user.id, username=username)
        return ResponseUpdate(message='Username actualizado')



    async def UserUpdateEmail(self, current_user: CurrentUser, email_api:EmailStr) -> ResponseUpdate:
        email = self.textutils.is_valid_and_safe_email(email_api)

        await self.userondb.update_user_entry(id=current_user.id, email=email)
        return ResponseUpdate(message='Email actualizado')



    async def UserUpdatePassword(self, current_user: CurrentUser, password_api:SecretStr) -> ResponseUpdate:
        password = hash_password(password_api.get_secret_value())

        await self.userondb.update_user_entry(id=current_user.id, password_hash=password)
        return ResponseUpdate(message='Contraseña actualizada')



    async def UserUpdateTier(self, current_user: CurrentUser, username_api:str, tier_api: uuid.UUID) -> ResponseUpdate:
        current_tier = await self.userondb.get_user_tier(current_user.id)
        if current_tier != "admin":
            raise HTTPException(status_code=403, detail="No tienes permiso para actualizar el tier de otros usuarios.")

        user = await self.userondb.get_user_entry_for_login(username_api)
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        await self.userondb.update_user_entry(id=user.id, usertier=tier_api)
        return ResponseUpdate(message='Tier actualizado')



    async def UserUpdateProfilePic(self, current_user: CurrentUser, pic_api: str) -> ResponseUpdate:
        profile_picture = self.textutils.sanitize_text(pic_api)

        await self.userondb.update_user_entry(id=current_user.id, profile_picture=profile_picture)
        return ResponseUpdate(message='Profile Pic actualizada')



    async def UserUpdateBio(self, current_user: CurrentUser, bio_api: str) -> ResponseUpdate:
        bio = self.textutils.sanitize_text(bio_api)

        await self.userondb.update_user_entry(id=current_user.id, biography=bio)
        return ResponseUpdate(message='Bio actualizada')



    async def login(self, username_api: str, password_api: SecretStr, response: Response) -> ResponseLogin:
        user = await self.userondb.get_user_entry_for_login(username_api)

        fake_hash = "$argon2id$v=19$m=65536,t=3,p=4$vS7p6p6p6p6p6p6p6p6p6g$6p6p6p6p6p6p6p6p6p6p6p6p6p6p6p6p6p6p6p6p6p6"

        try:
            verify_password(
                password_api.get_secret_value(), 
                user.password_hash if user else fake_hash
            )
        
            if user is None:
                raise HashMismatch("User not found")

        except (HashMismatch, InvalidHashFormat):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid credentials"
            )
        except HashError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal authentication error"
            )

        access_token, refresh_token = TokenService(user.id, user.username).generate_tokens()

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=PRODUCTION_MODE,
            samesite="lax",
            max_age=60 * 60 * 24 * 7,
        )

        return ResponseLogin(
            access_token=access_token,
            username=user.username  # Use the username from DB for consistency
        )



    def reauth(self, current_user: CurrentUser) -> ResponseReauth:
        new_access_token, _ = TokenService(current_user.id, current_user.username).generate_tokens()
        return ResponseReauth(
            access_token=new_access_token,
        )



    def logout(self, response: Response) -> ResponseLogout:
        response.delete_cookie("refresh_token")
        return ResponseLogout(message="Log out correcto")
