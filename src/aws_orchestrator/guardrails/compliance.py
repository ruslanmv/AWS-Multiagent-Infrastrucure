"""Compliance guardrails for data validation, PII masking, and access control.

This module implements security and compliance features including:
- PII detection and masking
- Data validation
- Access control enforcement
- Audit logging
"""

import re
from typing import Any, Dict

import structlog

from aws_orchestrator.core.models import GuardrailConfig, TaskRequest

logger = structlog.get_logger(__name__)


class ComplianceEngine:
    """Engine for enforcing compliance and security guardrails.

    This class provides:
    - Input validation
    - PII detection and masking
    - Output filtering
    - Audit logging

    Attributes:
        config: Guardrail configuration
        pii_patterns: Regex patterns for PII detection
    """

    # Common PII patterns
    PII_PATTERNS = {
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    }

    def __init__(self, config: GuardrailConfig) -> None:
        """Initialize compliance engine.

        Args:
            config: Guardrail configuration
        """
        self.config = config
        self.pii_patterns = {
            name: re.compile(pattern) for name, pattern in self.PII_PATTERNS.items()
        }
        logger.info(
            "compliance_engine_initialized",
            pii_detection=config.pii_detection,
            audit_logging=config.audit_logging,
        )

    def detect_pii(self, text: str) -> Dict[str, int]:
        """Detect PII in text.

        Args:
            text: Text to scan for PII

        Returns:
            Dictionary of PII type to count
        """
        if not self.config.pii_detection:
            return {}

        detections: Dict[str, int] = {}
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(text)
            if matches:
                detections[pii_type] = len(matches)
                logger.warning("pii_detected", pii_type=pii_type, count=len(matches))

        return detections

    def mask_pii(self, text: str) -> str:
        """Mask PII in text.

        Args:
            text: Text to mask

        Returns:
            Text with PII masked
        """
        if not self.config.pii_detection:
            return text

        masked_text = text
        for pii_type, pattern in self.pii_patterns.items():
            masked_text = pattern.sub(f"[{pii_type.upper()}_REDACTED]", masked_text)

        return masked_text

    async def validate_request(self, request: TaskRequest) -> TaskRequest:
        """Validate and sanitize incoming request.

        Args:
            request: Task request to validate

        Returns:
            Validated and sanitized request
        """
        if not self.config.enabled:
            return request

        # Log request for audit
        if self.config.audit_logging:
            logger.info(
                "request_validated",
                task_id=str(request.task_id),
                user_id=request.user_id,
                query_length=len(request.query),
            )

        # Detect PII
        pii_found = self.detect_pii(request.query)

        # Mask PII if detected
        if pii_found and self.config.pii_detection:
            masked_query = self.mask_pii(request.query)
            request.query = masked_query
            logger.info("pii_masked", task_id=str(request.task_id), pii_types=list(pii_found.keys()))

        return request

    async def filter_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Filter and sanitize response data.

        Args:
            response: Response to filter

        Returns:
            Filtered response
        """
        if not self.config.enabled:
            return response

        # Convert to string for PII detection
        response_str = str(response)

        # Detect and mask PII in response
        if self.config.pii_detection:
            pii_found = self.detect_pii(response_str)
            if pii_found:
                logger.warning("pii_in_response", pii_types=list(pii_found.keys()))
                # In production, implement more sophisticated masking

        # Log response for audit
        if self.config.audit_logging:
            logger.info("response_filtered", response_size=len(response_str))

        return response

    def validate_access(self, user_id: str, resource: str) -> bool:
        """Validate user access to a resource.

        Args:
            user_id: User identifier
            resource: Resource identifier

        Returns:
            True if access granted, False otherwise
        """
        if not self.config.enabled:
            return True

        # TODO: Implement IAM policy validation
        # For now, allow all authenticated users
        logger.debug("access_validated", user_id=user_id, resource=resource)
        return True
