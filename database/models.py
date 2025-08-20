from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field

EscrowState = Literal[
    "INITIATED",
    "PENDING_DEPOSIT",
    "FUNDS_HELD",
    "DELIVERED",
    "UNDER_REVIEW",
    "RELEASED",
    "REFUNDED",
    "CANCELLED",
]


class UserModel(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    full_name: Optional[str] = None
    kyc_status: Literal["unverified", "pending", "verified", "rejected"] = "unverified"
    reputation: int = 0


class BlacklistModel(BaseModel):
    telegram_id: int
    reason: str
    severity: int = 1
    active: bool = True
    evidence_urls: List[str] = []


class EscrowModel(BaseModel):
    buyer_id: int
    seller_id: int
    item_type: Literal["digital", "physical", "service"] = "digital"
    description: str
    amount_cents: int
    currency: str = "INR"
    state: EscrowState = "INITIATED"
    provider_ref: Optional[str] = None
    group_id: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
