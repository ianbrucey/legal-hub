"""
API Client modules for Legal Intelligence Hub.

This package contains client implementations for external services:
- s3_client: AWS S3 upload functionality
- gemini_client: Gemini CLI wrapper and File Search SDK

Note: Court Listener client is imported from courtlistener-api/ package
(reusing existing infrastructure instead of duplicating).
"""

from .s3_client import S3Client, S3UploadResult
from .gemini_client import (
    GeminiCLI,
    GeminiFileSearch,
    WebSearchResult,
    FileStoreResult,
    FileUploadResult,
    FileSearchResult,
    Citation,
)

__all__ = [
    "S3Client",
    "S3UploadResult",
    "GeminiCLI",
    "GeminiFileSearch",
    "WebSearchResult",
    "FileStoreResult",
    "FileUploadResult",
    "FileSearchResult",
    "Citation",
]

