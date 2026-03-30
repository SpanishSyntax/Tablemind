from uuid import UUID
from typing import Optional

from fastapi import HTTPException
from shared_models import User, UserTier
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

class UsersDb:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_user_duplicity(self, username: str, email: str) -> Optional[User]:
        """Check the username for a user to see if it already exists in the database"""
        try:
            result = await self.db.execute(
                select(User).options(selectinload(User.tier)).where((User.username == username) | (User.email == email))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error adquiriendo usuario desde db: {str(e)}"
            )

    async def create_user_entry(self, username: str, email: str, passwd: str) -> User:
        """Create an entry in the database for the user"""
        try:
            result = await self.db.execute(
                select(UserTier).options(selectinload(User.tier)).where(UserTier.label == "free")
            )
            free_tier = result.scalar_one_or_none()
            if not free_tier:
                raise HTTPException(status_code=404, detail="El tipo no existe.")
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error obteniendo tipo de usuario: {str(e)}"
            )

        user = User(
            usertier=free_tier.id, username=username, email=email, password_hash=passwd
        )
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error creando usuario en db: {str(e)}"
            )

    async def get_user_entry_for_login(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).options(selectinload(User.tier)).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_user_tier(self, user_id: UUID) -> Optional[str]:
        """Returns the name of the user's tier by user ID in a single query."""
        result = await self.db.execute(
            select(UserTier.label)
            .join(User, User.tier == UserTier.id)
            .where(User.id == user_id)
        )
        tier = result.scalar_one_or_none()

        if tier:
            return tier
        else:
            raise HTTPException(
                status_code=404, detail="Tipo de usuario o usuario no encontrados"
            )

    async def get_user_entry(self, user_id: UUID) -> Optional[User]:
        """Returns the tier of a user by ID."""
        result = await self.db.execute(select(User).options(selectinload(User.tier)).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def update_user_entry(
        self,
        id: UUID,
        username: Optional[str] = None,
        usertier: Optional[UUID] = None,
        email: Optional[str] = None,
        password_hash: Optional[str] = None,
        profile_picture: Optional[str] = None,
        biography: Optional[str] = None,
    ) -> User:
        """Update fields for a user dynamically if they are provided"""
        try:
            result = await self.db.execute(select(User).options(selectinload(User.tier)).where(User.id == id))
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(status_code=404, detail="El usuario no existe.")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error adquiriendo usuario desde db: {str(e)}"
            )

        # Dynamically update fields if they are provided
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if password_hash is not None:
            user.password_hash = password_hash

        try:
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error actualizando el usuario: {str(e)}"
            )

    async def delete_user_entry(self, username: str, email: str, passwd: str) -> None:
        """Delete an entry in the database for the user"""
        try:
            result = await self.db.execute(
                select(User).where(or_(User.username == username, User.email == email))
            )
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=400, detail="El user no existe.")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error adquiriendo usuario desde db: {str(e)}"
            )
        if user.password_hash != passwd:
            raise HTTPException(status_code=400, detail="La contraseña no es correcta")
        else:
            try:
                await self.db.delete(user)
                await self.db.commit()
            except Exception as e:
                await self.db.rollback()
                raise HTTPException(
                    status_code=500, detail=f"Error eliminando el user: {str(e)}"
                )
