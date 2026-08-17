"""Custom exception classes for Aviator AI Autonomous Portfolio Rebalancing Agent."""


class AviatorAIError(Exception):
    """Base exception class for all Aviator AI errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class ConfigurationError(AviatorAIError):
    """Raised when there is an issue loading or parsing configuration settings."""

    pass


class ValidationError(AviatorAIError):
    """Raised when data validation constraints fail."""

    pass


class SecurityDataError(AviatorAIError):
    """Raised when security master data creation or validation fails."""

    pass


class ClientProfileError(AviatorAIError):
    """Raised when client profile generation or validation fails."""

    pass


class PortfolioAllocationError(AviatorAIError):
    """Raised when portfolio composition or allocation rules fail."""

    pass


class MarketSimulationError(AviatorAIError):
    """Raised when market data simulation or covariance calculations fail."""

    pass


class StorageError(AviatorAIError):
    """Raised when data persistence or loading operations fail."""

    pass
