"""Custom exceptions for JobFit AI"""

class JobFitException(Exception):
    """Base exception for JobFit errors"""
    pass


class PDFExtractionError(JobFitException):
    """Raised when PDF text extraction fails"""
    pass


class EmbeddingError(JobFitException):
    """Raised when embedding generation fails"""
    pass


class LLMError(JobFitException):
    """Raised when LLM API calls fail"""
    pass


class ValidationError(JobFitException):
    """Raised when input validation fails"""
    pass
