import hashlib
import re
import unicodedata
from decimal import Decimal
from typing import List

from fastapi import File, HTTPException, UploadFile
from models import FileTypesEnum
from shared_models import FileType


class MediaUtils:
    def sanitize_filename(self, text: str) -> str:
        if not text or text.strip() == "":
            raise HTTPException(
                status_code=400, detail="El nombre del archivo no puede estar vacío."
            )

        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r'[<>:"/\\|?*]', "_", text)  # Replace unsafe file chars
        text = re.sub(r"[\x00-\x1f\x7f]", "", text)  # Remove control characters
        text = text.replace(" ", "_")
        text = re.sub(r"_+", "_", text)
        text = text.strip("_")

        if not text or text in {".", ".."}:
            raise HTTPException(status_code=400, detail="Nombre de archivo inválido.")

        if len(text) > 255:
            raise HTTPException(
                status_code=400,
                detail="El nombre del archivo excede el límite de 255 caracteres.",
            )

        return text

    def check_file_type(self, filetype: str) -> FileType:
        if not filetype:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Archivo sin formato.",
                    "content_type": filetype,
                    "allowed": [m.value for m in FileTypesEnum],
                },
            )
        elif filetype not in FileTypesEnum:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Formato de archivo no soportado.",
                    "content_type": filetype,
                    "allowed": [m.value for m in FileTypesEnum],
                },
            )
        else:
            return FileType(name=filetype)

    def determine_subpath(self, filetype: FileType):
        if filetype in {FileTypesEnum.PNG, FileTypesEnum.JPEG}:
            return "images"
        elif filetype == FileTypesEnum.MP4:
            return "videos"
        elif filetype in {
            FileTypesEnum.EXCEL_1,
            FileTypesEnum.EXCEL_2,
            FileTypesEnum.OPEN_EXCEL_1,
            FileTypesEnum.OPEN_EXCEL_2,
            FileTypesEnum.CSV,
            FileTypesEnum.TSV,
        }:
            return "tables"
        else:
            raise HTTPException(status_code=400, detail="FileType desconocido.")

    # def check_user_quota(self, filesize: int, user) -> None:
    #     if user.freespace + filesize > MediaQuota(user.user_type):
    #         raise HTTPException(status_code=403, detail="No tienes suficiente espacio en tu cuota de almacenamiento.")

    def generate_file_hash(self, file: UploadFile) -> tuple[str, int]:
        try:
            hasher = hashlib.sha256()
            total_size = 0
            while chunk := file.file.read(8192):
                hasher.update(chunk)
                total_size += len(chunk)
            file.file.seek(0)

            if total_size == 0:
                raise HTTPException(status_code=400, detail="Archivo vacío.")

            return hasher.hexdigest(), total_size
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error en generación de hash: {str(e)}"
            )

    def validate_file(self, allowed_types: List[str]):
        async def validator(file: UploadFile = File(...)) -> UploadFile:
            if not file:
                raise HTTPException(
                    status_code=400, detail="No se ha proporcionado ningún archivo."
                )
            if not file.filename:
                raise HTTPException(
                    status_code=400, detail="El archivo no tiene nombre."
                )
            if not file.content_type:
                raise HTTPException(
                    status_code=400,
                    detail="No se pudo determinar el tipo de contenido del archivo.",
                )
            if file.content_type not in allowed_types:
                json_ready_allowed = [
                    [item if not isinstance(item, Decimal) else int(item) for item in rule]
                    for rule in allowed_types
                ]
                raise HTTPException(
                    status_code=422,
                    detail={
                        "error": "Tipo de archivo no permitido.",
                        "content_type": file.content_type,
                        "allowed": json_ready_allowed,
                    },
                )
            return file

        return validator
