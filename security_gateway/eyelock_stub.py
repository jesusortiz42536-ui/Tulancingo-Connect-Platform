"""
EyeLock™ Biometric Authentication — Integration Stubs.

These stubs define the interface contracts for EyeLock™ iris-based
biometric authentication. All methods raise ``NotImplementedError`` by
default and must be overridden (or replaced) with real SDK calls when the
EyeLock™ vendor library is integrated.

Typical flow
------------
1. Enroll a user: ``gateway.enroll(user_id, iris_payload)``
2. Authenticate: ``result = gateway.authenticate(user_id, iris_payload)``
3. Revoke on account closure: ``gateway.revoke(user_id)``
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional


class AuthStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NOT_ENROLLED = "not_enrolled"
    REVOKED = "revoked"
    ERROR = "error"


@dataclass
class BiometricProfile:
    """
    Stores a (stub) biometric template for a single user.

    In production the ``template_hash`` would be a one-way transform of the
    iris scan produced by the EyeLock™ SDK — raw biometric data must never
    be stored in plaintext.
    """

    user_id: str
    template_hash: str          # SHA-256 hex digest of the iris payload (stub)
    profile_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    enrolled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


@dataclass
class AuthResult:
    """Result object returned by every authentication attempt."""

    user_id: str
    status: AuthStatus
    message: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_successful(self) -> bool:
        return self.status == AuthStatus.SUCCESS


class BiometricAuthGateway:
    """
    Stub gateway for EyeLock™ iris biometric authentication.

    All public methods correspond to endpoints in the EyeLock™ REST/SDK API.
    Replace the stub bodies with real vendor SDK calls during integration.

    Example::

        gateway = BiometricAuthGateway()
        gateway.enroll("user-123", b"<raw-iris-scan-bytes>")
        result = gateway.authenticate("user-123", b"<raw-iris-scan-bytes>")
        assert result.is_successful
    """

    # ------------------------------------------------------------------
    # Stub configuration
    # ------------------------------------------------------------------
    _VENDOR = "EyeLock™"
    _SDK_VERSION = "stub-0.0.0"      # replace with real SDK version on integration

    def __init__(self) -> None:
        # In production this registry would be persisted in a secure HSM or
        # encrypted database — never in-memory plain dicts.
        self._profiles: Dict[str, BiometricProfile] = {}

    # ------------------------------------------------------------------
    # Public API stubs
    # ------------------------------------------------------------------

    def enroll(self, user_id: str, iris_payload: bytes) -> BiometricProfile:
        """
        Enroll a user's iris biometric template with EyeLock™.

        **Stub behaviour**: hashes the raw payload with SHA-256 and stores
        the digest as the "template". Real implementation must call the
        EyeLock™ enrollment endpoint and store only the vendor-issued
        template reference.

        Args:
            user_id: Unique identifier for the user.
            iris_payload: Raw iris scan bytes captured by EyeLock™ hardware.

        Returns:
            A :class:`BiometricProfile` representing the enrolled template.

        Raises:
            ValueError: If the user is already enrolled.
            NotImplementedError: When called with ``_use_real_sdk=True``
                (reserved for future integration).
        """
        if user_id in self._profiles and self._profiles[user_id].is_active:
            raise ValueError(f"User '{user_id}' is already enrolled.")

        # TODO: Replace with real EyeLock™ SDK enrollment call, e.g.:
        #   template_ref = eyelock_sdk.enroll(user_id, iris_payload)
        template_hash = self._hash_payload(iris_payload)
        profile = BiometricProfile(user_id=user_id, template_hash=template_hash)
        self._profiles[user_id] = profile
        return profile

    def authenticate(self, user_id: str, iris_payload: bytes) -> AuthResult:
        """
        Verify a user's identity against their enrolled iris template.

        **Stub behaviour**: compares the SHA-256 hash of the provided payload
        to the stored template hash. Real implementation must call the
        EyeLock™ match/verify endpoint.

        Args:
            user_id: Unique identifier for the user.
            iris_payload: Raw iris scan bytes to verify.

        Returns:
            An :class:`AuthResult` with the outcome of the verification.
        """
        # TODO: Replace with real EyeLock™ SDK verification call, e.g.:
        #   match = eyelock_sdk.verify(user_id, iris_payload)
        profile = self._profiles.get(user_id)

        if profile is None:
            return AuthResult(
                user_id=user_id,
                status=AuthStatus.NOT_ENROLLED,
                message="User has no enrolled biometric profile.",
            )

        if not profile.is_active:
            return AuthResult(
                user_id=user_id,
                status=AuthStatus.REVOKED,
                message="User's biometric profile has been revoked.",
            )

        candidate_hash = self._hash_payload(iris_payload)
        if candidate_hash == profile.template_hash:
            return AuthResult(
                user_id=user_id,
                status=AuthStatus.SUCCESS,
                message="Biometric authentication successful.",
            )

        return AuthResult(
            user_id=user_id,
            status=AuthStatus.FAILURE,
            message="Iris scan did not match the enrolled template.",
        )

    def revoke(self, user_id: str) -> None:
        """
        Revoke a user's biometric profile (e.g. on account deletion).

        **Stub behaviour**: marks the profile as inactive. Real implementation
        must also call the EyeLock™ template deletion endpoint to ensure the
        biometric data is purged from vendor systems.

        Args:
            user_id: Unique identifier for the user whose profile to revoke.

        Raises:
            KeyError: If no profile exists for the given user.
        """
        # TODO: Call eyelock_sdk.delete_template(user_id) before local removal.
        profile = self._profiles.get(user_id)
        if profile is None:
            raise KeyError(f"No biometric profile found for user '{user_id}'.")
        profile.is_active = False

    def get_profile(self, user_id: str) -> Optional[BiometricProfile]:
        """
        Return the biometric profile for a user, or ``None`` if not enrolled.

        Args:
            user_id: Unique identifier for the user.
        """
        return self._profiles.get(user_id)

    def health_check(self) -> dict:
        """
        Return a health/status snapshot of the EyeLock™ gateway.

        **Stub behaviour**: returns static metadata. Real implementation
        should ping the EyeLock™ service endpoint and report latency.
        """
        # TODO: Replace with real EyeLock™ SDK health/status call.
        return {
            "vendor": self._VENDOR,
            "sdk_version": self._SDK_VERSION,
            "status": "stub — not connected to EyeLock™ service",
            "enrolled_profiles": len(self._profiles),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _hash_payload(payload: bytes) -> str:
        """
        Produce a SHA-256 hex digest of the raw iris payload.

        Used only in stub mode. In production, the vendor SDK performs
        feature extraction and stores the result as an opaque template
        reference — the platform should never handle raw biometric bytes.
        """
        return hashlib.sha256(payload).hexdigest()
