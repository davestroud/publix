"""
S3 service for uploading data, reports, and cached results
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Service:
    """Service for uploading data to S3"""

    def __init__(self):
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "publix-expansion-data")
        self.region = os.getenv("S3_REGION", os.getenv("AWS_REGION", "us-east-1"))

        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                "s3",
                region_name=self.region,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
            logger.info(f"S3 service initialized for bucket: {self.bucket_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize S3 client: {e}")
            self.s3_client = None

    def upload_json(
        self,
        data: Dict | List,
        key: str,
        folder: str = "data",
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Upload JSON data to S3

        Args:
            data: Data to upload (dict or list)
            key: S3 key (filename)
            folder: Folder prefix (data, reports, cache, scraped-data)
            metadata: Optional metadata dict

        Returns:
            True if successful, False otherwise
        """
        if not self.s3_client:
            logger.warning("S3 client not available, skipping upload")
            return False

        try:
            # Ensure key has .json extension
            if not key.endswith(".json"):
                key = f"{key}.json"

            # Construct full key with folder
            full_key = f"{folder}/{key}"

            # Convert to JSON string
            json_data = json.dumps(data, indent=2, default=str)

            # Prepare metadata
            upload_metadata = {
                "uploaded_at": datetime.utcnow().isoformat(),
                **(metadata or {}),
            }

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=full_key,
                Body=json_data.encode("utf-8"),
                ContentType="application/json",
                Metadata={k: str(v) for k, v in upload_metadata.items()},
            )

            logger.info(f"Uploaded {full_key} to S3 ({len(json_data)} bytes)")
            return True

        except ClientError as e:
            logger.error(f"Failed to upload {key} to S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading to S3: {e}", exc_info=True)
            return False

    def upload_stores(
        self,
        stores: List[Dict],
        store_type: str = "publix",
        state: Optional[str] = None,
    ) -> bool:
        """
        Upload store data to S3

        Args:
            stores: List of store dictionaries
            store_type: Type of store (publix, walmart, kroger)
            state: Optional state filter

        Returns:
            True if successful
        """
        if not stores:
            logger.info(f"No {store_type} stores to upload")
            return True

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        state_suffix = f"_{state}" if state else ""
        key = f"{store_type}_stores{state_suffix}_{timestamp}.json"

        metadata = {
            "store_type": store_type,
            "count": len(stores),
            "state": state or "all",
        }

        return self.upload_json(
            data=stores,
            key=key,
            folder="scraped-data",
            metadata=metadata,
        )

    def upload_collection_results(self, results: Dict, region: str) -> bool:
        """
        Upload complete collection results to S3

        Args:
            results: Collection results dict with publix_stores, competitor_stores, etc.
            region: Region identifier

        Returns:
            True if successful
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        key = f"collection_results_{region}_{timestamp}.json"

        metadata = {
            "region": region,
            "publix_count": len(results.get("publix_stores", [])),
            "competitor_count": sum(
                len(v) for v in results.get("competitor_stores", {}).values()
            ),
        }

        return self.upload_json(
            data=results,
            key=key,
            folder="data",
            metadata=metadata,
        )

    def upload_report(self, report_data: Dict, report_type: str = "analysis") -> bool:
        """
        Upload analysis report to S3

        Args:
            report_data: Report data dictionary
            report_type: Type of report (analysis, prediction, etc.)

        Returns:
            True if successful
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        key = f"{report_type}_report_{timestamp}.json"

        return self.upload_json(
            data=report_data,
            key=key,
            folder="reports",
            metadata={"report_type": report_type},
        )

    def upload_cache(self, cache_key: str, cache_data: Dict) -> bool:
        """
        Upload cached data to S3

        Args:
            cache_key: Cache key identifier
            cache_data: Cached data

        Returns:
            True if successful
        """
        key = f"{cache_key}.json"

        return self.upload_json(
            data=cache_data,
            key=key,
            folder="cache",
            metadata={"cache_key": cache_key},
        )

    def list_objects(self, folder: str = "", prefix: str = "") -> List[str]:
        """
        List objects in S3 bucket

        Args:
            folder: Folder to list (data, reports, cache, scraped-data)
            prefix: Additional prefix filter

        Returns:
            List of object keys
        """
        if not self.s3_client:
            return []

        try:
            full_prefix = f"{folder}/{prefix}" if folder else prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=full_prefix
            )

            keys = [obj["Key"] for obj in response.get("Contents", [])]
            return keys

        except ClientError as e:
            logger.error(f"Failed to list S3 objects: {e}")
            return []

    def get_object(self, key: str) -> Optional[Dict]:
        """
        Download and parse JSON object from S3

        Args:
            key: S3 object key

        Returns:
            Parsed JSON data or None
        """
        if not self.s3_client:
            return None

        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response["Body"].read().decode("utf-8")
            return json.loads(content)

        except ClientError as e:
            logger.error(f"Failed to get S3 object {key}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {key}: {e}")
            return None


# Global instance
_s3_service = None


def get_s3_service() -> S3Service:
    """Get or create S3 service instance"""
    global _s3_service
    if _s3_service is None:
        _s3_service = S3Service()
    return _s3_service
