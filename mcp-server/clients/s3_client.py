"""
AWS S3 Client for uploading research reports.

Provides async-compatible S3 upload functionality with auto-key generation.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any
from functools import partial

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseModel

from config import config


class S3UploadResult(BaseModel):
    """Result of an S3 upload operation."""
    s3_uri: str
    key: str
    version_id: str | None = None


class S3Client:
    """
    Client for uploading research reports to AWS S3.
    
    Supports both explicit key specification and auto-generation
    based on timestamp for organized storage.
    """
    
    def __init__(
        self,
        bucket: str | None = None,
        region: str | None = None,
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
    ):
        """
        Initialize S3 client.
        
        Args:
            bucket: Default bucket name (falls back to config)
            region: AWS region (falls back to config)
            access_key_id: AWS access key (falls back to config/env)
            secret_access_key: AWS secret key (falls back to config/env)
        """
        self.default_bucket = bucket or config.s3.default_bucket
        self.region = region or config.s3.region
        
        # Build boto3 client kwargs
        client_kwargs: dict[str, Any] = {"region_name": self.region}
        
        # Only pass credentials if explicitly provided or in config
        ak = access_key_id or config.s3.access_key_id
        sk = secret_access_key or config.s3.secret_access_key
        if ak and sk:
            client_kwargs["aws_access_key_id"] = ak
            client_kwargs["aws_secret_access_key"] = sk
        
        self._client = boto3.client("s3", **client_kwargs)
    
    def _generate_key(self, prefix: str = "reports") -> str:
        """
        Generate a timestamp-based S3 key.
        
        Format: {prefix}/YYYY/MM/DD/report-{timestamp}.md
        """
        now = datetime.now(timezone.utc)
        timestamp = int(now.timestamp())
        return f"{prefix}/{now.year}/{now.month:02d}/{now.day:02d}/report-{timestamp}.md"
    
    async def upload_report(
        self,
        report: str,
        bucket: str | None = None,
        key: str | None = None,
        metadata: dict[str, str] | None = None,
    ) -> S3UploadResult:
        """
        Upload a research report to S3.
        
        Args:
            report: Report content (markdown string)
            bucket: S3 bucket name (uses default if not provided)
            key: S3 object key (auto-generates if not provided)
            metadata: Optional metadata to attach to the object
            
        Returns:
            S3UploadResult with s3_uri, key, and version_id
            
        Raises:
            ClientError: If upload fails
        """
        bucket = bucket or self.default_bucket
        key = key or self._generate_key()
        
        # Prepare put_object kwargs
        put_kwargs: dict[str, Any] = {
            "Bucket": bucket,
            "Key": key,
            "Body": report.encode("utf-8"),
            "ContentType": "text/markdown; charset=utf-8",
        }
        
        if metadata:
            put_kwargs["Metadata"] = metadata
        
        # Run blocking boto3 call in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            partial(self._client.put_object, **put_kwargs)
        )
        
        return S3UploadResult(
            s3_uri=f"s3://{bucket}/{key}",
            key=key,
            version_id=response.get("VersionId"),
        )
    
    async def check_bucket_exists(self, bucket: str | None = None) -> bool:
        """Check if the specified bucket exists and is accessible."""
        bucket = bucket or self.default_bucket
        
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                partial(self._client.head_bucket, Bucket=bucket)
            )
            return True
        except ClientError:
            return False

