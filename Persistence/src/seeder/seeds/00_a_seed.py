"""Poblado de log action types"""
import os
import uuid
from enum import Enum

from fastapi import HTTPException
from shared_db import SessionSync
from shared_models import User, UserTier
from shared_utils import encrypt, get_logger, hash_password
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


def upgrade() -> None:
    with SessionSync() as session:
        """Populate default tiers"""
        default_tiers = [
            {
                "label": "free",
                "storage_quota": 100_000_000,
            },
            {
                "label": "premium",
                "storage_quota": 1_000_000_000,
            },
            {
                "label": "admin",
                "storage_quota": 10_000_000_000,
            },
        ]
        try:
            for tier in default_tiers:
                result = session.execute(
                    select(UserTier).where(UserTier.label == tier["label"])
                )
                if not result.scalar_one_or_none():
                    session.add(UserTier(id=uuid.uuid4(), **tier))

            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error seedeando db para usertypes: {str(e)}"
            )

        """Populate default users"""
        result = session.execute(
            select(UserTier).where(UserTier.label == "admin")
        )
        admin_tier = result.scalar_one_or_none()
        if not admin_tier:
            raise HTTPException(status_code=404, detail="El tipo no existe.")
        default_users = [
            {
                "usertier": admin_tier.id,
                "username": "root",
                "email": "root@TableMind.com",
                "password_hash": hash_password(PASS_ROOT_USER),
                "profile_picture": "",
                "biography": "",
                "media_usage": 0,
            },
        ]
        try:
            for user in default_users:
                result = session.execute(
                    select(User).where(User.username == user["username"])
                )
                if not result.scalar_one_or_none():
                    session.add(User(id=uuid.uuid4(), **user))

            session.commit()
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=500, detail=f"Error seedeando db para users: {str(e)}"
            )

        """Populate models"""
        default_models = [
            {
                "name": "Google Gemini 2 flash",
                "provider": LLMProviders.GOOGLE,
                "encoder": "gemini-2.5-flash-preview-04-17",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": True,
            },
            {
                "name": "OpenAI GPT-4",
                "provider": LLMProviders.OPENAI,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
            },
            {
                "name": "Meta LLaMA 2 13B",
                "provider": LLMProviders.META,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
            },
            {
                "name": "Cohere Command R+",
                "provider": LLMProviders.COHERE,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
            },
            {
                "name": "Anthropic Claude 3",
                "provider": LLMProviders.ANTHROPIC,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
            },
            {
                "name": "AI21 Jurassic-1 Jumbo",
                "provider": LLMProviders.AI21,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
            },
            {
                "name": "Mistral 7B",
                "provider": LLMProviders.MISTRAL,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
            },
            {
                "name": "EleutherAI GPT-NeoX 20B",
                "provider": LLMProviders.ELEUTHERAI,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
            },
            {
                "name": "Hugging Face Bloom-176B",
                "provider": LLMProviders.HUGGINGFACE,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
            },
            {
                "name": "NVIDIA Megatron-Turing NLG 530B",
                "provider": LLMProviders.NVIDIA,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
            },
            {
                "name": "Amazon Bedrock Titan",
                "provider": LLMProviders.AMAZON,
                "encoder": "gpt-3.5-turbo",
                "temperature": 0.1,
                "top_p": 0.1,
                "endpoint_url": "https://generativelanguage.googleapis.com/",
                "cost_per_1m_input": 15,  # 0.15 dollars => 15 cents
                "cost_per_1m_output": 60,  # 0.60 dollars => 60 cents
                "max_input_tokens": 1_048_576,
                "max_output_tokens": 65_535,
                "is_active": False,
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
