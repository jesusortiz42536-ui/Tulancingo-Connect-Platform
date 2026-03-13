"""
Tests for the security_gateway (EyeLock™) module.
"""

import pytest

from security_gateway.eyelock_stub import AuthStatus, BiometricAuthGateway


SAMPLE_IRIS = b"sample-iris-scan-data-for-testing"
DIFFERENT_IRIS = b"different-iris-scan-data"


class TestBiometricAuthGateway:
    def test_enroll_and_authenticate_success(self):
        gw = BiometricAuthGateway()
        gw.enroll("user-1", SAMPLE_IRIS)
        result = gw.authenticate("user-1", SAMPLE_IRIS)
        assert result.is_successful
        assert result.status == AuthStatus.SUCCESS

    def test_authentication_failure_wrong_iris(self):
        gw = BiometricAuthGateway()
        gw.enroll("user-2", SAMPLE_IRIS)
        result = gw.authenticate("user-2", DIFFERENT_IRIS)
        assert not result.is_successful
        assert result.status == AuthStatus.FAILURE

    def test_authenticate_not_enrolled(self):
        gw = BiometricAuthGateway()
        result = gw.authenticate("ghost-user", SAMPLE_IRIS)
        assert result.status == AuthStatus.NOT_ENROLLED

    def test_duplicate_enrollment_raises(self):
        gw = BiometricAuthGateway()
        gw.enroll("user-3", SAMPLE_IRIS)
        with pytest.raises(ValueError):
            gw.enroll("user-3", SAMPLE_IRIS)

    def test_revoke_profile(self):
        gw = BiometricAuthGateway()
        gw.enroll("user-4", SAMPLE_IRIS)
        gw.revoke("user-4")
        result = gw.authenticate("user-4", SAMPLE_IRIS)
        assert result.status == AuthStatus.REVOKED

    def test_revoke_nonexistent_raises(self):
        gw = BiometricAuthGateway()
        with pytest.raises(KeyError):
            gw.revoke("nobody")

    def test_get_profile(self):
        gw = BiometricAuthGateway()
        assert gw.get_profile("no-user") is None
        gw.enroll("user-5", SAMPLE_IRIS)
        profile = gw.get_profile("user-5")
        assert profile is not None
        assert profile.user_id == "user-5"
        assert profile.is_active is True

    def test_health_check(self):
        gw = BiometricAuthGateway()
        health = gw.health_check()
        assert "vendor" in health
        assert health["vendor"] == "EyeLock™"
        assert health["enrolled_profiles"] == 0
        gw.enroll("user-6", SAMPLE_IRIS)
        health = gw.health_check()
        assert health["enrolled_profiles"] == 1
