"""An S3StorageService bucket/object-key design adapted for UUID private avatars.
Use a second client to sign the PUBLIC endpoint, never rewrite signed URL hosts.
No public bucket policy is created by this module.
"""
import base64
import os
import uuid
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException
PREFIX = 's3-private:'


def enabled():
    mode = os.getenv('AVATAR_STORAGE','database').strip().lower()
    if mode not in ('database','s3'):
        raise HTTPException(503,detail={'code':'STORAGE_CONFIG_INVALID','message':'AVATAR_STORAGE phải là database hoặc s3.'})
    return mode == 's3'


def client(public=False):
    endpoint = os.getenv('STORAGE_PUBLIC_ENDPOINT' if public else 'STORAGE_ENDPOINT','').strip()
    key = os.getenv('STORAGE_ACCESS_KEY','').strip()
    secret = os.getenv('STORAGE_SECRET_KEY','').strip()
    if not endpoint.startswith(('http://','https://')) or not key or not secret:
        raise HTTPException(503,detail={'code':'STORAGE_NOT_CONFIGURED','message':'Chưa cấu hình endpoint và khóa storage.'})
    return boto3.client('s3',endpoint_url=endpoint,aws_access_key_id=key,aws_secret_access_key=secret,
        region_name=os.getenv('STORAGE_REGION','us-east-1'),
        config=Config(signature_version='s3v4',s3={'addressing_style':'path'},connect_timeout=5,read_timeout=10,retries={'max_attempts':1}))


class S3StorageService:
    def upload_avatar(self, data_url, user_id):
        client(public=True) # Validate signing config before writing an object.
        raw = base64.b64decode(data_url.split(',',1)[1],validate=True)
        key = f'avatars/{user_id}/{uuid.uuid4().hex}.jpg'
        try:
            client().put_object(Bucket=os.getenv('STORAGE_PRIVATE_BUCKET','virtufit-private'), Key=key, Body=raw, ContentType='image/jpeg')
        except (BotoCoreError,ClientError):
            raise HTTPException(503,detail={'code':'STORAGE_UNAVAILABLE','message':'Không tải được ảnh lên storage.'})
        return PREFIX+key

    def avatar_url(self, reference):
        if not reference or not reference.startswith(PREFIX):
            return reference
        try:
            return client(public=True).generate_presigned_url('get_object',
                Params={'Bucket':os.getenv('STORAGE_PRIVATE_BUCKET','virtufit-private'),'Key':reference[len(PREFIX):]},ExpiresIn=1800)
        except (BotoCoreError,ClientError):
            raise HTTPException(503,detail={'code':'STORAGE_UNAVAILABLE','message':'Không tạo được URL ảnh.'})


storage_service = S3StorageService()
