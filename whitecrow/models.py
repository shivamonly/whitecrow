from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class InvestigationRequest(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    username: Optional[str] = None
    photo_path: Optional[str] = None


class ToolResult(BaseModel):
    tool: str
    status: str = "pending"
    result: dict = {}
    error: Optional[str] = None
    elapsed: float = 0.0


class Overview(BaseModel):
    confidence_score: int = 0
    matches_found: int = 0
    primary_name: Optional[str] = None
    primary_location: Optional[str] = None
    risk_flags: list[str] = []


class Identity(BaseModel):
    full_name: Optional[str] = None
    aliases: list[str] = []
    age: Optional[int] = None
    gender: Optional[str] = None
    dob: Optional[str] = None


class Contact(BaseModel):
    email_addresses: list[str] = []
    phone_numbers: list[str] = []
    addresses: list[str] = []


class SocialProfile(BaseModel):
    platform: str
    profile_url: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None


class Messaging(BaseModel):
    whatsapp: Optional[bool] = None
    telegram: Optional[bool] = None
    signal: Optional[bool] = None
    viber: Optional[bool] = None
    skype: Optional[str] = None


class DigitalPresence(BaseModel):
    social_media: list[SocialProfile] = []
    messaging: Messaging = Messaging()
    forums: list[SocialProfile] = []
    professional: list[SocialProfile] = []


class LocationData(BaseModel):
    current_city: Optional[str] = None
    gps_coordinates: list[dict] = []
    area_code: Optional[str] = None
    country: Optional[str] = None


class BreachEntry(BaseModel):
    service: str
    date: Optional[str] = None
    data_exposed: list[str] = []


class BreachData(BaseModel):
    breaches: list[BreachEntry] = []
    plaintext_passwords: list[str] = []
    pastebin_mentions: list[dict] = []


class PhotoMetadata(BaseModel):
    camera_model: Optional[str] = None
    datetime_original: Optional[str] = None
    gps: Optional[str] = None
    software: Optional[str] = None


class TimelineEntry(BaseModel):
    date: Optional[str] = None
    event: str
    source: str
    evidence_url: Optional[str] = None


class InvestigationResult(BaseModel):
    query: dict = {}
    overview: Overview = Overview()
    identity: Identity = Identity()
    contact: Contact = Contact()
    digital_presence: DigitalPresence = DigitalPresence()
    location: LocationData = LocationData()
    breach_data: BreachData = BreachData()
    photo_metadata: Optional[PhotoMetadata] = None
    timeline: list[TimelineEntry] = []
    raw_findings: dict[str, ToolResult] = {}
    report_metadata: dict = {}
