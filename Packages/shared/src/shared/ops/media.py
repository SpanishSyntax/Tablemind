import os
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, Sequence

import aiofiles
from fastapi import HTTPException, UploadFile
from shared_models import File, FileType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared_schemas import (
    ResponseMessage,
)


class MediaDb:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def check_duplicity(self, owner: UUID, filehash: str) -> Optional[File]:
        """Generate a hash for the file and check if it already exists in the database"""
        try:
            result = await self.db.execute(
                select(File).options(selectinload(File.type)).where(File.filehash == filehash, File.user_id == owner)
            )
            media = result.scalar_one_or_none()
            return media
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error revisando duplicidad de archivo: {str(e)}",
            )

    async def get_media_entry(self, id: UUID, owner: UUID) -> File:
        """Create an entry in the database for the uploaded file"""
        try:
            result = await self.db.execute(
                select(File).options(selectinload(File.type)).where(
                    File.id == id,
                    File.user_id == owner,
                )
            )
            media = result.scalar_one_or_none()
            if not media:
                raise HTTPException(status_code=404, detail="El archivo no existe.")
            return media
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error adquiriendo media desde db: {str(e)}"
            )

    async def get_all_media_entries(self, owner: UUID) -> Sequence[File]:
        """Create an entry in the database for the uploaded file"""
        try:
            result = await self.db.execute(
                select(File).options(selectinload(File.type)).where(
                    File.user_id == owner,
                )
            )
            media = result.scalars().all()
            if not media:
                raise HTTPException(status_code=404, detail="El archivo no existe.")
            return media
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error adquiriendo varios media desde db: {str(e)}",
            )

    async def create_media_entry(
        self,
        owner: UUID,
        filetype: FileType,
        filename: str,
        filepath: str,
        filehash: str,
        filesize: int,
    ) -> File:
        """Create an entry in the database for the uploaded file"""
        media = File(
            user_id=owner,
            type=filetype,
            filename=filename,
            filepath=filepath,
            filehash=filehash,
            filesize=filesize
        )
        try:
            self.db.add(media)
            await self.db.commit()
            await self.db.refresh(media)
            return media
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error creando el archivo en db: {str(e)}"
            )

    async def update_media_entry(
        self,
        id: UUID,
        owner: UUID,
        filetype: Optional[FileType] = None,
        filename: Optional[str] = None,
        filepath: Optional[str] = None,
        filehash: Optional[str] = None,
    ) -> File:
        """Create an entry in the database for the uploaded file"""
        try:
            result = await self.db.execute(
                select(File).options(selectinload(File.type)).where(
                    File.id == id,
                    File.user_id == owner,
                )
            )
            media = result.scalar_one_or_none()
            if not media:
                raise HTTPException(status_code=404, detail="El archivo no existe.")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error adquiriendo media desde db: {str(e)}"
            )

        if filetype is not None:
            media.type = filetype
        if filename is not None:
            media.filename = filename
        if filehash is not None:
            media.filehash = filehash
        if filepath is not None:
            media.filepath = filepath

        try:
            await self.db.commit()
            await self.db.refresh(media)
            return media
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error actualizando el archivo: {str(e)}"
            )

    async def delete_media_entry(self, id: UUID, owner: UUID) -> None:
        """Create an entry in the database for the uploaded file"""
        try:
            result = await self.db.execute(
                select(File).options(selectinload(File.type)).where(
                    File.id == id,
                    File.user_id == owner,
                )
            )
            media = result.scalar_one_or_none()
            if not media:
                raise HTTPException(status_code=404, detail="El archivo no existe.")
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error adquiriendo media desde db: {str(e)}"
            )

        try:
            await self.db.delete(media)
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error eliminando el archivo: {str(e)}"
            )


class MediaDisk:
    async def save_file(
        self,
        user_id: UUID,
        file: UploadFile,
        filename: str,
        filepath: str,
    ) -> ResponseMessage:
        """Save the file to disk"""

        if not filename:
            raise HTTPException(
                status_code=400, detail="No se ha proporcionado un nombre de archivo."
            )

        os.makedirs(filepath, exist_ok=True)

        file_path = os.path.join(filepath, filename)

        try:
            async with aiofiles.open(file_path, "wb") as f:
                while chunk := await file.read(1024 * 1024):
                    await f.write(chunk)
        except OSError as e:
            raise HTTPException(
                status_code=500, detail=f"Error al guardar el archivo: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error inesperado al guardar el archivo: {str(e)}",
            )

        return ResponseMessage(message="Archivo guardado exitosamente.")

    async def rename_file(
        self,
        user_id: UUID,
        old_filename: str,
        new_filename: str,
        filepath: str,
    ) -> ResponseMessage:
        """Overwrite the file to disk"""

        if not new_filename:
            raise HTTPException(
                status_code=400, detail="No se ha proporcionado un nombre de archivo."
            )

        old_file_path = os.path.join(filepath, old_filename)
        new_file_path = os.path.join(filepath, new_filename)

        try:
            os.rename(old_file_path, new_file_path)
        except OSError as e:
            raise HTTPException(
                status_code=500, detail=f"Error al renombrar el archivo: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error inesperado al guardar el archivo: {str(e)}",
            )

        return ResponseMessage(message="Archivo guardado exitosamente.")

    async def delete_file(
        self,
        user_id: UUID,
        filename: str,
        filepath: str,
    ) -> ResponseMessage:
        """Save the file to disk"""

        if not filename:
            raise HTTPException(
                status_code=400, detail="No se ha proporcionado un nombre de archivo."
            )
        file_path = os.path.join(filepath, filename)

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return ResponseMessage(message="Archivo eliminado exitosamente.")
            else:
                raise HTTPException(status_code=404, detail="Archivo no encontrado")
        except OSError as e:
            raise HTTPException(
                status_code=500, detail=f"Error al eliminar el archivo: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error inesperado al eliminar el archivo: {str(e)}",
            )
