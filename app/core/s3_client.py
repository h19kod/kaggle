import boto3
from botocore.config import Config as BotoConfig
from botocore.exceptions import ClientError
from fastapi import UploadFile
from app.core.config import settings


class S3Service:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=BotoConfig(signature_version="s3v4"),
            use_ssl=settings.S3_USE_SSL,
        )
        self.bucket = settings.S3_BUCKET_NAME

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)

    def upload_file(self, file: UploadFile, key: str) -> str:
        self._ensure_bucket()
        self.client.upload_fileobj(file.file, self.bucket, key)
        return f"{settings.S3_ENDPOINT}/{self.bucket}/{key}"

    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expiration,
        )

    def delete_file(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)


s3_service = S3Service()
