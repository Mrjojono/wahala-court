"""Post generation for resolved cases."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.engine import generate_posts

router = APIRouter(tags=["posts"])


class PostGenerateRequest(BaseModel):
	caseFile: dict[str, Any] = Field(default_factory=dict)
	verdict: dict[str, Any] = Field(default_factory=dict)
	peopleShare: int = 0
	formats: list[str] = Field(default_factory=lambda: ["caption", "whatsapp", "dev"])


@router.post("/posts/generate")
async def posts_generate(body: PostGenerateRequest):
	result = await generate_posts(
		{
			"caseFile": body.caseFile,
			"verdict": body.verdict,
			"peopleShare": body.peopleShare,
		},
		formats=body.formats,
	)
	return result
