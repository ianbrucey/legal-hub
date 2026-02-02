"""
Gemini Client implementations.

Provides:
- GeminiFileSearch: Wrapper for Gemini File Search API (RAG)
"""

import os
import asyncio
from typing import Any
from pathlib import Path

from pydantic import BaseModel
from google import genai
from google.genai import types


class FileStoreResult(BaseModel):
    """Result from creating a file store."""
    store_name: str
    store_id: str


class FileUploadResult(BaseModel):
    """Result from uploading a file."""
    file_id: str
    file_name: str
    status: str


class Citation(BaseModel):
    """A citation from file search."""
    file_name: str
    chunk: str
    score: float | None = None


class FileSearchResult(BaseModel):
    """Result from file search query."""
    answer: str
    citations: list[Citation]


class GeminiFileSearch:
    """
    Wrapper for Gemini File Search API (RAG).
    
    Uses the google-genai SDK to create file stores, upload documents,
    and perform semantic search queries.
    """
    
    def __init__(self, api_key: str | None = None):
        """
        Initialize Gemini File Search client.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            # Will use default credentials if available
            self.client = genai.Client()
    
    async def create_store(self, name: str, display_name: str | None = None) -> FileStoreResult:
        """
        Create a new file search store.
        
        Args:
            name: Unique name for the store
            display_name: Human-readable display name (defaults to name)
            
        Returns:
            FileStoreResult with store_name and store_id
        """
        display = display_name or name
        
        # Run in executor since SDK may be blocking
        loop = asyncio.get_event_loop()
        store = await loop.run_in_executor(
            None,
            lambda: self.client.file_search_stores.create(
                config={"display_name": display}
            )
        )
        
        # Extract ID from store name (format: fileSearchStores/{id})
        store_id = store.name.split("/")[-1] if "/" in store.name else store.name
        
        return FileStoreResult(
            store_name=store.name,
            store_id=store_id,
        )
    
    async def upload(
        self,
        store_name: str,
        file_path: str,
        display_name: str | None = None,
    ) -> FileUploadResult:
        """
        Upload a document to a file search store.
        
        Args:
            store_name: File search store resource name
            file_path: Local path to file to upload
            display_name: Optional display name for the file
            
        Returns:
            FileUploadResult with file_id, file_name, status
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        name = display_name or path.name
        
        loop = asyncio.get_event_loop()
        operation = await loop.run_in_executor(
            None,
            lambda: self.client.file_search_stores.upload_to_file_search_store(
                file=str(path),
                file_search_store_name=store_name,
                config={"display_name": name}
            )
        )

        # Wait for operation to complete
        result = await loop.run_in_executor(None, operation.result)

        return FileUploadResult(
            file_id=getattr(result, "name", "unknown"),
            file_name=name,
            status="completed",
        )

    async def query(
        self,
        store_name: str,
        query: str,
        model: str = "gemini-2.5-flash",
    ) -> FileSearchResult:
        """
        Query documents in a file search store using semantic RAG.

        Args:
            store_name: File search store resource name
            query: Natural language query
            model: Gemini model to use for generation

        Returns:
            FileSearchResult with answer and citations
        """
        loop = asyncio.get_event_loop()

        # Build the request with file search tool
        response = await loop.run_in_executor(
            None,
            lambda: self.client.models.generate_content(
                model=model,
                contents=query,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(
                                file_search_store_names=[store_name]
                            )
                        )
                    ]
                )
            )
        )

        # Extract answer text
        answer = ""
        if response.candidates and response.candidates[0].content.parts:
            answer = response.candidates[0].content.parts[0].text

        # Extract citations from grounding metadata if available
        citations = []
        grounding = getattr(response.candidates[0], "grounding_metadata", None)
        if grounding and hasattr(grounding, "grounding_chunks"):
            for chunk in grounding.grounding_chunks:
                citations.append(Citation(
                    file_name=getattr(chunk, "source", "unknown"),
                    chunk=getattr(chunk, "text", ""),
                    score=getattr(chunk, "relevance_score", None),
                ))

        return FileSearchResult(
            answer=answer,
            citations=citations,
        )

