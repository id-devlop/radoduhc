
from fastapi import APIRouter
import boto3, os, io, time

router = APIRouter()

@router.post("/s3")
def export_s3():
    # demo upload to S3-compatible endpoint (can be MinIO etc.)
    bucket = os.getenv("S3_BUCKET","exposure-exports")
    key = f"exports/audit-{int(time.time())}.csv"
    s3 = boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT_URL") or None)
    # Put a tiny demo object
    data = "id,type,user,role,timestamp,payload\n1,DEMO,system,system,now,{}\n"
    s3.put_object(Bucket=bucket, Key=key, Body=data.encode("utf-8"))
    return {"location": f"s3://{bucket}/{key}"}
