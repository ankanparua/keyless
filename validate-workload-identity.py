#!/usr/bin/env python3
"""
Workload Identity Validator
Verifies OIDC federation is working correctly without long-lived keys
"""
import boto3
import sys
import os
from botocore.exceptions import NoCredentialsError, ClientError

def check_environment():
    """Check if running in expected environment"""
    if os.getenv('GITHUB_ACTIONS') == 'true':
        print("✅ Running in GitHub Actions Environment")
    else:
        print("⚠️  Running locally (Ensure AWS_PROFILE is set)")

def test_sts_identity():
    """Test STS GetCallerIdentity"""
    try:
        client = boto3.client('sts')
        response = client.get_caller_identity()
        arn = response.get('Arn', '')
        
        if 'assumed-role' in arn:
            print(f"✅ Identity Verified: {arn}")
            return True
        else:
            print(f"⚠️  Identity is not a assumed role: {arn}")
            return False
    except NoCredentialsError:
        print("❌ No Credentials Found (OIDC may have failed)")
        return False
    except ClientError as e:
        print(f"❌ AWS API Error: {e}")
        return False

def test_s3_access(bucket_name):
    """Test S3 Read Access"""
    try:
        client = boto3.client('s3')
        client.head_bucket(Bucket=bucket_name)
        print(f"✅ S3 Access Verified: {bucket_name}")
        return True
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '403':
            print(f"⚠️  S3 Access Denied (Check Policy): {bucket_name}")
            return False
        elif error_code == '404':
            print(f"⚠️  S3 Bucket Not Found: {bucket_name}")
            return False
        else:
            print(f"❌ S3 Error: {e}")
            return False

def main():
    print("🔍 Validating Workload Identity Configuration...")
    check_environment()
    
    success = True
    success &= test_sts_identity()
    
    bucket = os.getenv('S3_BUCKET_NAME', 'test-bucket')
    success &= test_s3_access(bucket)
    
    if success:
        print("\n🎉 Workload Identity Validation Successful")
        sys.exit(0)
    else:
        print("\n⚠️  Validation Complete with Warnings/Errors")
        sys.exit(1)

if __name__ == '__main__':
    main()
