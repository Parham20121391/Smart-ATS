import json
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi import HTTPException, status
from app.services.network import AsyncNetworkService
import logging

logger = logging.getLogger(__name__)


class ExtractedResumeSchema(BaseModel):
    skills: List[str] = Field(description="لیست دقیق مهارت‌های فنی استخراج شده")
    github_username: Optional[str] = Field(None, description="شناسه گیت‌هاب کارجو")
    linkedin_url: Optional[str] = Field(None, description="آدرس کامل پروفایل لینکدین")
    experience_years: float = Field(0.0, description="مجموع سال‌های سابقه کار")


class OllamaAIService:

    SYSTEM_PROMPT = (
        "You are an expert ATS data extraction agent. "
        "Analyze the provided resume text and return a strict JSON object. "
        "The JSON must contain exactly these fields: "
        "skills (array of strings), "
        "github_username (string or null), "
        "linkedin_url (string or null), "
        "experience_years (float). "
        "Do not include any markdown, prose, thinking tags, or backticks. "
        "Return ONLY valid raw JSON and nothing else."
    )

    @classmethod
    async def extract_resume_metadata(cls, resume_text: str) -> ExtractedResumeSchema:
        client = AsyncNetworkService.get_client()
        prompt = f"Resume Text:\n{resume_text[:3000]}\n\nStrict JSON Output:"
        payload = {
            "model": "qwen3-coder:30b",
            "prompt": prompt,
            "system": cls.SYSTEM_PROMPT,
            "stream": False,
            "format": "json"
        }

        try:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=120.0
            )

            if response.status_code != 200:
                logger.error(f"Ollama server error: {response.status_code}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"موتور Ollama خطای {response.status_code} بازگرداند."
                )

            result = response.json()
            raw_json = result.get("response", "{}")

            try:
                clean_json = raw_json.strip()

                if "<think>" in clean_json:
                    think_end = clean_json.rfind("</think>")
                    if think_end != -1:
                        clean_json = clean_json[think_end + 8:].strip()

                if "```" in clean_json:
                    parts = clean_json.split("```")
                    for part in parts:
                        if part.startswith("json"):
                            clean_json = part[4:].strip()
                            break
                        elif "{" in part:
                            clean_json = part.strip()
                            break

                start = clean_json.find("{")
                end = clean_json.rfind("}") + 1
                if start != -1 and end > start:
                    clean_json = clean_json[start:end]

                parsed_data = json.loads(clean_json)
                return ExtractedResumeSchema(**parsed_data)

            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"JSON parse error: {str(e)} | Raw: {raw_json[:200]}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="خروجی مدل هوش مصنوعی قابل پارس نیست."
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ollama connection error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ارتباط با موتور Ollama برقرار نشد."
            )

    @classmethod
    def check_digital_footprint(cls, extracted_data: ExtractedResumeSchema) -> dict:
        tasks_to_queue = []

        if extracted_data.github_username:
            tasks_to_queue.append({
                "type": "github_verification",
                "username": extracted_data.github_username
            })
            logger.info(f"GitHub verification queued for: {extracted_data.github_username}")

        if extracted_data.linkedin_url:
            tasks_to_queue.append({
                "type": "linkedin_verification",
                "url": extracted_data.linkedin_url
            })
            logger.info(f"LinkedIn verification queued for: {extracted_data.linkedin_url}")

        return {
            "tasks_queued": len(tasks_to_queue),
            "tasks": tasks_to_queue
        }