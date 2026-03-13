"""
security_gateway — EyeLock™ Biometric Authentication integration module.

Provides integration stubs for the EyeLock™ iris-based biometric
authentication system. Replace stub implementations with real SDK calls
once the EyeLock™ vendor SDK is available.
"""

from .eyelock_stub import BiometricAuthGateway, BiometricProfile, AuthResult

__all__ = ["BiometricAuthGateway", "BiometricProfile", "AuthResult"]
