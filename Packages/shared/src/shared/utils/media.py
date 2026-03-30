import hashlib
import re
import unicodedata
from decimal import Decimal
from typing import List

from fastapi import File, HTTPException, UploadFile
from models import FileTypesEnum
from shared_models import FileType


class MediaUtils:
    def _sanitize_for_json(self, data):
        """Recursively converts Decimals to ints and Tuples to Lists for JSON safety."""
        if isinstance(data, Decimal):
            return int(data)
        if isinstance(data, dict):
            return {k: self._sanitize_for_json(v) for k, v in data.items()}
        if isinstance(data, (list, tuple)):
            return [self._sanitize_for_json(item) for item in data]
        return data

    def sanitize_filename(self, text: str) -> str:
        if not text or text.strip() == "":
            raise HTTPException(status_code=400, detail="El nombre del archivo no puede estar vacío.")

        text = unicodedata.normalize("NFKC", text)
        text = re.sub(r'[<>:"/\\|?*]', "_", text)
        text = re.sub(r"[\x00-\x1f\x7f]", "", text)
        text = text.replace(" ", "_")
        text = re.sub(r"_+", "_", text)
        text = text.strip("_")

        if not text or text in {".", ".."}:
            raise HTTPException(status_code=400, detail="Nombre de archivo inválido.")
        if len(text) > 255:
            raise HTTPException(status_code=400, detail="El nombre del archivo excede el límite de 255 caracteres.")
        return text

    def check_file_type(self, filetype: str) -> FileType:
        matched_enum_member = next(
            (m for m in FileTypesEnum if m.value[0] == filetype), 
            None
        )
    
        if not filetype or not matched_enum_member:
            raise HTTPException(
                status_code=400,
                detail=self._sanitize_for_json({
                    "error": "Formato de archivo no soportado.",
                    "content_type": filetype,
                    "allowed": [m.value for m in FileTypesEnum],
                }),
            )

        mime, ext, cat, size = matched_enum_member.value

        return FileType(
            label=matched_enum_member.name, # e.g., "EXCEL_2"
            mime_type=mime,                 # e.g., "application/vnd..."
            extension=ext,                  # e.g., ".xlsx"
            category=cat,                   # e.g., "tabular"
            max_size=size                   # e.g., Decimal('20971520')
        )

    def determine_subpath(self, filetype: FileType):
        # Comparison logic remains the same, but ensure you compare against the Enum members
        # Note: filetype here is the Pydantic model from check_file_type
        ft_name = filetype.label 
        
        if ft_name in {FileTypesEnum.PNG.value[0], FileTypesEnum.JPEG.value[0]}:
            return "images"
        elif ft_name == FileTypesEnum.MP4.value[0]:
            return "videos"
        elif ft_name in [m.value[0] for m in FileTypesEnum if m.value[2] == "tabular"]:
            return "tables"
        else:
            raise HTTPException(status_code=400, detail="FileType desconocido.")

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
            if isinstance(e, HTTPException): raise e
            raise HTTPException(status_code=500, detail=f"Error en generación de hash: {str(e)}")

    def validate_file(self, allowed_types: List[str]):
        async def validator(file: UploadFile = File(...)) -> UploadFile:
            if not file or not file.filename or not file.content_type:
                raise HTTPException(status_code=400, detail="Archivo inválido o incompleto.")
            
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=422,
                    detail=self._sanitize_for_json({
                        "error": "Tipo de archivo no permitido.",
                        "content_type": file.content_type,
                        "allowed": allowed_types,
                    }),
                )
            return file
        return validator
