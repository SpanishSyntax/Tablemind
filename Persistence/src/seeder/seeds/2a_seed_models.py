"""Poblado de log action types"""

import os
import uuid
from enum import Enum

from fastapi import HTTPException
from shared_db import SessionSync
from shared_utils import encrypt, get_logger
from sqlalchemy import select

from models import APIKey_on_db, Model_on_db

logger = get_logger("seed/log_action_types")
PASS_ROOT_USER = os.environ["PASS_ROOT_USER"]
KEY_API_GEMINI = os.environ["KEY_API_GEMINI"]


class LLMProviders(str, Enum):
    OPENAI = "OpenAI"
    GOOGLE = "Google"
    META = "Meta"
    COHERE = "Cohere"
    MISTRAL = "Mistral"
    ELEUTHERAI = "EleutherAI"
    AI21 = "AI21 Labs"
    HUGGINGFACE = "Hugging Face"
    NVIDIA = "NVIDIA"
    AMAZON = "Amazon"
    ANTHROPIC = "Anthropic"
    DEEPSEEK = "DeepSeek"


def upgrade() -> None:
    with SessionSync() as session:
        """Populate models"""
        default_models = [
            {
                "name": "Google Gemini 2.0 Flash",
                "provider": LLMProviders.GOOGLE,
                "encoder": "gemini-2.0-flash-exp",  # Use 'gemini-2.0-flash' for stable
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 10,  # $0.10 USD
                "cost_per_1m_output": 30,  # $0.30 USD
                "max_input_tokens": 2_097_152,  # 2M context is the new standard
                "max_output_tokens": 16384,
                "is_active": True,
            },
            {
                "name": "OpenAI GPT-5 (Omni)",
                "provider": LLMProviders.OPENAI,
                "encoder": "gpt-5",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://api.openai.com/v1/",
                "cost_per_1m_input": 150,  # $1.50
                "cost_per_1m_output": 500,  # $5.00
                "max_input_tokens": 256_000,
                "max_output_tokens": 8192,
                "is_active": True,
            },
            {
                "name": "Anthropic Claude 4 Opus",
                "provider": LLMProviders.ANTHROPIC,
                "encoder": "claude-4-opus-latest",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://api.anthropic.com/v1/messages",
                "cost_per_1m_input": 500,  # $5.00
                "cost_per_1m_output": 1500,  # $15.00
                "max_input_tokens": 500_000,
                "max_output_tokens": 12288,
                "is_active": True,
            },
            {
                "name": "Meta LLaMA 4 405B",
                "provider": LLMProviders.META,
                "encoder": "llama-4-405b",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://api.groq.com/openai/v1",
                "cost_per_1m_input": 40,
                "cost_per_1m_output": 70,
                "max_input_tokens": 256_000,
                "max_output_tokens": 4096,
                "is_active": False,
            },
            {
                "name": "DeepSeek-V3 (Coder)",
                "provider": LLMProviders.DEEPSEEK,
                "encoder": "deepseek-v3",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://api.deepseek.com/",
                "cost_per_1m_input": 14,  # Highly aggressive pricing
                "cost_per_1m_output": 28,
                "max_input_tokens": 128_000,
                "max_output_tokens": 8192,
                "is_active": True,
            },
        ]
        try:
            for model in default_models:
                result = session.execute(
                    select(Model_on_db).where(Model_on_db.name == model["name"])
                )
                if not result.scalar_one_or_none():
                    session.add(Model_on_db(id=uuid.uuid4(), **model))

            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error seedeando db para models: {str(e)}"
            )

        """Populate default tiers"""
        result = session.execute(
            select(Model_on_db).where(Model_on_db.name == "Google Gemini 2 flash")
        )
        model = result.scalar_one_or_none()
        if not model:
            raise HTTPException(status_code=404, detail="El modelo no existe.")
        default_keys = [
            {
                "model_id": model.id,
                "api_key": encrypt(KEY_API_GEMINI),
            },
        ]
        try:
            for key in default_keys:
                result = session.execute(
                    select(APIKey_on_db).where(APIKey_on_db.model_id == key["model_id"])
                )
                if not result.scalar_one_or_none():
                    session.add(APIKey_on_db(id=uuid.uuid4(), **key))

            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error seedeando db para usertypes: {str(e)}"
            )
