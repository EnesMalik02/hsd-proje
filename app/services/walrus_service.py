"""
Walrus Blockchain Storage Service

This service provides integration with Walrus decentralized storage protocol
for storing and retrieving chat messages and media files on the blockchain.

Walrus is a decentralized storage protocol built on Sui blockchain.
"""

import httpx
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class WalrusService:
    """Service for interacting with Walrus decentralized storage."""
    
    def __init__(
        self,
        publisher_url: str,
        aggregator_url: str,
        epochs: int = 5,
        timeout: int = 30
    ):
        """
        Initialize Walrus service.
        
        Args:
            publisher_url: Walrus publisher endpoint URL
            aggregator_url: Walrus aggregator endpoint URL
            epochs: Number of epochs to store the blob (default: 5)
            timeout: HTTP request timeout in seconds
        """
        self.publisher_url = publisher_url.rstrip('/')
        self.aggregator_url = aggregator_url.rstrip('/')
        self.epochs = epochs
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
    
    def store_blob(self, data: bytes, content_type: str = "application/octet-stream") -> Optional[Dict[str, Any]]:
        """
        Store data as a blob on Walrus blockchain.
        
        Args:
            data: Binary data to store
            content_type: MIME type of the data
            
        Returns:
            Dict containing blob_id and other metadata, or None if failed
        """
        try:
            url = f"{self.publisher_url}/v1/blobs"
            params = {"epochs": self.epochs}
            headers = {"Content-Type": content_type}
            
            logger.info(f"Storing blob to Walrus: {len(data)} bytes, type: {content_type}")
            
            response = self.client.put(
                url,
                params=params,
                headers=headers,
                content=data
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Walrus API response structure
                if "newlyCreated" in result:
                    blob_info = result["newlyCreated"]["blobObject"]
                    blob_id = blob_info["blobId"]
                    
                    logger.info(f"Blob stored successfully: {blob_id}")
                    
                    return {
                        "blob_id": blob_id,
                        "size": blob_info.get("size"),
                        "encoding_type": blob_info.get("encodingType"),
                        "certified_epoch": blob_info.get("certifiedEpoch"),
                        "storage_type": "walrus",
                        "stored_at": datetime.utcnow().isoformat()
                    }
                elif "alreadyCertified" in result:
                    blob_info = result["alreadyCertified"]["blobObject"]
                    blob_id = blob_info["blobId"]
                    
                    logger.info(f"Blob already exists: {blob_id}")
                    
                    return {
                        "blob_id": blob_id,
                        "size": blob_info.get("size"),
                        "encoding_type": blob_info.get("encodingType"),
                        "certified_epoch": blob_info.get("certifiedEpoch"),
                        "storage_type": "walrus",
                        "already_existed": True
                    }
                else:
                    logger.error(f"Unexpected Walrus response: {result}")
                    return None
            else:
                logger.error(f"Walrus store failed: {response.status_code} - {response.text}")
                # Log full response for debugging
                logger.error(f"Request URL: {url}")
                logger.error(f"Request params: {params}")
                return None
                
        except httpx.TimeoutException:
            logger.error("Walrus store timeout")
            return None
        except Exception as e:
            logger.error(f"Walrus store error: {str(e)}")
            return None
    
    def read_blob(self, blob_id: str) -> Optional[bytes]:
        """
        Read blob data from Walrus blockchain.
        
        Args:
            blob_id: The blob ID to retrieve
            
        Returns:
            Binary data of the blob, or None if failed
        """
        try:
            url = f"{self.aggregator_url}/v1/{blob_id}"
            
            logger.info(f"Reading blob from Walrus: {blob_id}")
            
            response = self.client.get(url)
            
            if response.status_code == 200:
                logger.info(f"Blob read successfully: {blob_id}, size: {len(response.content)} bytes")
                return response.content
            else:
                logger.error(f"Walrus read failed: {response.status_code} - {response.text}")
                return None
                
        except httpx.TimeoutException:
            logger.error(f"Walrus read timeout for blob: {blob_id}")
            return None
        except Exception as e:
            logger.error(f"Walrus read error: {str(e)}")
            return None
    
    def get_blob_info(self, blob_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata information about a blob.
        
        Args:
            blob_id: The blob ID
            
        Returns:
            Dict containing blob metadata, or None if failed
        """
        try:
            # Try to read the blob to verify it exists
            data = self.read_blob(blob_id)
            
            if data:
                return {
                    "blob_id": blob_id,
                    "size": len(data),
                    "exists": True,
                    "aggregator_url": f"{self.aggregator_url}/v1/{blob_id}"
                }
            else:
                return {
                    "blob_id": blob_id,
                    "exists": False
                }
                
        except Exception as e:
            logger.error(f"Error getting blob info: {str(e)}")
            return None
    
    def store_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Convenience method to store text data.
        
        Args:
            text: Text string to store
            
        Returns:
            Dict containing blob_id and metadata
        """
        return self.store_blob(text.encode('utf-8'), content_type="text/plain; charset=utf-8")
    
    def read_text(self, blob_id: str) -> Optional[str]:
        """
        Convenience method to read text data.
        
        Args:
            blob_id: The blob ID
            
        Returns:
            Text string, or None if failed
        """
        data = self.read_blob(blob_id)
        if data:
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                logger.error(f"Failed to decode blob {blob_id} as UTF-8")
                return None
        return None
    
    def store_json(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convenience method to store JSON data.
        
        Args:
            data: Dictionary to store as JSON
            
        Returns:
            Dict containing blob_id and metadata
        """
        json_str = json.dumps(data, ensure_ascii=False)
        return self.store_blob(json_str.encode('utf-8'), content_type="application/json")
    
    def read_json(self, blob_id: str) -> Optional[Dict[str, Any]]:
        """
        Convenience method to read JSON data.
        
        Args:
            blob_id: The blob ID
            
        Returns:
            Dictionary, or None if failed
        """
        data = self.read_blob(blob_id)
        if data:
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Failed to decode blob {blob_id} as JSON: {str(e)}")
                return None
        return None
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Singleton instance will be created in config
walrus_service: Optional[WalrusService] = None


def get_walrus_service() -> Optional[WalrusService]:
    """Get the global Walrus service instance."""
    return walrus_service


def init_walrus_service(publisher_url: str, aggregator_url: str, epochs: int = 5) -> WalrusService:
    """
    Initialize the global Walrus service instance.
    
    Args:
        publisher_url: Walrus publisher endpoint
        aggregator_url: Walrus aggregator endpoint
        epochs: Number of epochs for storage
        
    Returns:
        Initialized WalrusService instance
    """
    global walrus_service
    walrus_service = WalrusService(publisher_url, aggregator_url, epochs)
    logger.info(f"Walrus service initialized: publisher={publisher_url}, aggregator={aggregator_url}")
    return walrus_service
