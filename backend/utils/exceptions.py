class StartupIQError(Exception):
    """Base exception for all StartupIQ errors."""


class ValidationError(StartupIQError):
    """Raised when input validation fails."""


class PromptError(StartupIQError):
    """Raised for prompt-related failures."""


class PromptNotFoundError(PromptError):
    """Raised when a prompt file is not found."""


class ToolError(StartupIQError):
    """Raised when a tool execution fails."""


class PipelineError(StartupIQError):
    """Raised when the validation pipeline encounters an error."""


class APIError(StartupIQError):
    """Raised when an API-level error occurs."""
