"""Chambre du conseil + ADN du pote."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.engine import deliberate_chamber, extract_voice, build_depot, write_friend_letter

router = APIRouter(tags=["chamber"])


class ChamberRequest(BaseModel):
	case: dict[str, Any] = Field(default_factory=dict)
	transcript: list[dict[str, str]] = Field(default_factory=list)
	peopleVote: str = "coupable"
	mode: str = "chaos"
	voice: dict[str, Any] | None = None


class VoiceRequest(BaseModel):
	raw: str = ""
	accusedName: str = ""


class DepotRequest(BaseModel):
	friendName: str = ""
	raw: str = ""


class LetterRequest(BaseModel):
	friendName: str = ""
	case: dict[str, Any] = Field(default_factory=dict)
	peopleVote: str = "coupable"
	verdict: dict[str, Any] = Field(default_factory=dict)


@router.post("/chamber/deliberate")
async def chamber_deliberate(body: ChamberRequest):
	return await deliberate_chamber(
		case=body.case,
		transcript=body.transcript,
		people_vote=body.peopleVote,
		mode=body.mode,
		voice=body.voice,
	)


@router.post("/voice/extract")
async def voice_extract(body: VoiceRequest):
	return await extract_voice(raw=body.raw, accused_name=body.accusedName)


@router.post("/depot/build")
async def depot_build(body: DepotRequest):
	return await build_depot(friend_name=body.friendName, raw=body.raw)


@router.post("/letter/write")
async def letter_write(body: LetterRequest):
	return await write_friend_letter(
		friend_name=body.friendName,
		case=body.case,
		people_vote=body.peopleVote,
		verdict=body.verdict,
	)
