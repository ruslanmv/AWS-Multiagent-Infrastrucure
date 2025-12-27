"""Unit tests for ComplianceEngine."""

import pytest

from aws_orchestrator.core.models import GuardrailConfig, TaskRequest
from aws_orchestrator.guardrails.compliance import ComplianceEngine


class TestComplianceEngine:
    """Test ComplianceEngine functionality."""

    @pytest.fixture
    def compliance_engine(self) -> ComplianceEngine:
        """Create a compliance engine for testing."""
        config = GuardrailConfig(
            enabled=True,
            pii_detection=True,
            audit_logging=True,
        )
        return ComplianceEngine(config)

    def test_detect_pii_email(self, compliance_engine: ComplianceEngine) -> None:
        """Test PII detection for email addresses."""
        text = "Contact me at john.doe@example.com for details"
        detections = compliance_engine.detect_pii(text)

        assert "email" in detections
        assert detections["email"] == 1

    def test_detect_pii_phone(self, compliance_engine: ComplianceEngine) -> None:
        """Test PII detection for phone numbers."""
        text = "Call me at 555-123-4567 or 555.987.6543"
        detections = compliance_engine.detect_pii(text)

        assert "phone" in detections
        assert detections["phone"] == 2

    def test_detect_pii_ssn(self, compliance_engine: ComplianceEngine) -> None:
        """Test PII detection for SSN."""
        text = "My SSN is 123-45-6789"
        detections = compliance_engine.detect_pii(text)

        assert "ssn" in detections
        assert detections["ssn"] == 1

    def test_mask_pii_email(self, compliance_engine: ComplianceEngine) -> None:
        """Test PII masking for email addresses."""
        text = "Contact me at john.doe@example.com"
        masked = compliance_engine.mask_pii(text)

        assert "john.doe@example.com" not in masked
        assert "[EMAIL_REDACTED]" in masked

    def test_mask_pii_multiple(self, compliance_engine: ComplianceEngine) -> None:
        """Test PII masking for multiple types."""
        text = "Call 555-123-4567 or email john@example.com"
        masked = compliance_engine.mask_pii(text)

        assert "555-123-4567" not in masked
        assert "john@example.com" not in masked
        assert "[PHONE_REDACTED]" in masked
        assert "[EMAIL_REDACTED]" in masked

    @pytest.mark.asyncio
    async def test_validate_request(self, compliance_engine: ComplianceEngine) -> None:
        """Test request validation and PII masking."""
        request = TaskRequest(
            user_id="test-user",
            query="Contact me at secret@example.com",
        )

        validated = await compliance_engine.validate_request(request)

        assert "[EMAIL_REDACTED]" in validated.query
        assert "secret@example.com" not in validated.query

    @pytest.mark.asyncio
    async def test_filter_response(self, compliance_engine: ComplianceEngine) -> None:
        """Test response filtering."""
        response = {
            "status": "success",
            "data": "Processing complete",
        }

        filtered = await compliance_engine.filter_response(response)

        assert filtered is not None
        assert "status" in filtered

    def test_validate_access(self, compliance_engine: ComplianceEngine) -> None:
        """Test access validation."""
        has_access = compliance_engine.validate_access("user-123", "resource-456")
        assert has_access is True

    def test_disabled_pii_detection(self) -> None:
        """Test with PII detection disabled."""
        config = GuardrailConfig(enabled=True, pii_detection=False)
        engine = ComplianceEngine(config)

        text = "Email: test@example.com"
        detections = engine.detect_pii(text)
        masked = engine.mask_pii(text)

        assert len(detections) == 0
        assert masked == text
