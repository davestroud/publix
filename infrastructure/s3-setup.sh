#!/bin/bash
# Script to create and configure S3 bucket for Publix Expansion Predictor

set -e

BUCKET_NAME="publix-expansion-data"
REGION="${AWS_REGION:-us-east-1}"

echo "Creating S3 bucket: $BUCKET_NAME in region: $REGION"

# Check if bucket already exists
if aws s3 ls "s3://$BUCKET_NAME" 2>/dev/null; then
    echo "⚠️  Bucket $BUCKET_NAME already exists!"
    exit 0
fi

# Create bucket
echo "Creating bucket..."
aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"

# Enable versioning
echo "Enabling versioning..."
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled \
    --region "$REGION"

# Enable encryption
echo "Enabling server-side encryption..."
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}' \
    --region "$REGION"

# Block public access (security best practice)
echo "Configuring public access block..."
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
    --region "$REGION"

# Create folder structure
echo "Creating folder structure..."
aws s3api put-object --bucket "$BUCKET_NAME" --key "data/" --region "$REGION"
aws s3api put-object --bucket "$BUCKET_NAME" --key "reports/" --region "$REGION"
aws s3api put-object --bucket "$BUCKET_NAME" --key "cache/" --region "$REGION"
aws s3api put-object --bucket "$BUCKET_NAME" --key "scraped-data/" --region "$REGION"

echo ""
echo "=========================================="
echo "S3 Bucket Created Successfully!"
echo "=========================================="
echo "Bucket Name: $BUCKET_NAME"
echo "Region: $REGION"
echo "Versioning: Enabled"
echo "Encryption: AES256"
echo "Public Access: Blocked"
echo ""
echo "Folder Structure:"
echo "  - data/          (General data storage)"
echo "  - reports/        (Generated reports)"
echo "  - cache/          (Cached results)"
echo "  - scraped-data/   (Web scraping results)"
echo ""
echo "Add to your .env file:"
echo "S3_BUCKET_NAME=$BUCKET_NAME"
echo ""

