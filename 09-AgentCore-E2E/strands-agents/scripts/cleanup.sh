#!/bin/bash

set -e
set -o pipefail

# ----- Config -----
BUCKET_NAME=${1:-customersupport112}
INFRA_STACK_NAME=${2:-CustomerSupportStackInfra}
COGNITO_STACK_NAME=${3:-CustomerSupportStackCognito}
REGION=${AWS_REGION:-${AWS_DEFAULT_REGION:-$(aws configure get region)}}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>&1 || true)
FULL_BUCKET_NAME="${BUCKET_NAME}-${ACCOUNT_ID}-${REGION}"
ZIP_FILE="lambda.zip"
S3_KEY="lambda.zip"

if [ -z "$REGION" ] || [ "$REGION" = "None" ]; then
    echo "❌ Failed to determine AWS region. Export AWS_REGION, for example: export AWS_REGION=us-east-1"
    exit 1
fi

if [ $? -ne 0 ] || [ -z "$ACCOUNT_ID" ] || [ "$ACCOUNT_ID" = "None" ]; then
    echo "❌ Failed to get AWS Account ID. Please check your AWS credentials and network connectivity."
    echo "Error: $ACCOUNT_ID"
    exit 1
fi

# ----- Confirm Deletion -----
read -p "⚠️ Are you sure you want to delete stacks '$INFRA_STACK_NAME', '$COGNITO_STACK_NAME' and clean up S3? (y/N): " confirm || confirm=""
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "❌ Cleanup cancelled."
  exit 1
fi

empty_stack_bucket() {
  local stack_name=$1
  local output_key=$2
  local bucket_name

  bucket_name=$(aws cloudformation describe-stacks \
    --stack-name "$stack_name" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='${output_key}'].OutputValue | [0]" \
    --output text 2>/dev/null || true)

  if [ -n "$bucket_name" ] && [ "$bucket_name" != "None" ]; then
    echo "🧹 Emptying s3://$bucket_name before stack deletion..."
    aws s3 rm "s3://$bucket_name" --recursive || true
  fi
}

delete_stack_if_exists() {
  local stack_name=$1

  if ! aws cloudformation describe-stacks --stack-name "$stack_name" --region "$REGION" >/dev/null 2>&1; then
    echo "ℹ️ Stack $stack_name already deleted."
    return 0
  fi

  echo "🧨 Deleting stack: $stack_name..."
  aws cloudformation delete-stack --stack-name "$stack_name" --region "$REGION"
  echo "⏳ Waiting for $stack_name to be deleted..."
  aws cloudformation wait stack-delete-complete --stack-name "$stack_name" --region "$REGION"
  echo "✅ Stack $stack_name deleted."
}

# ----- 1. Delete CloudFormation stacks -----
empty_stack_bucket "$INFRA_STACK_NAME" "S3DataBucketName"
delete_stack_if_exists "$INFRA_STACK_NAME"

delete_stack_if_exists "$COGNITO_STACK_NAME"

# ----- 2. Delete zip file from S3 -----
echo "🧹 Deleting all contents of s3://$FULL_BUCKET_NAME..."
aws s3 rm "s3://$FULL_BUCKET_NAME" --recursive || echo "⚠️ Failed to clean bucket or it is already empty."

# ----- 3. Optionally delete the bucket -----
read -p "🪣 Do you want to delete the bucket '$FULL_BUCKET_NAME'? (y/N): " delete_bucket || delete_bucket=""
if [[ "$delete_bucket" == "y" || "$delete_bucket" == "Y" ]]; then
  echo "🚮 Deleting bucket $FULL_BUCKET_NAME..."
  aws s3 rb "s3://$FULL_BUCKET_NAME" --force
  echo "✅ Bucket deleted."
else
  echo "🪣 Bucket retained: $FULL_BUCKET_NAME"
fi

# ----- 4. Clean up local zip file -----
echo "🗑️ Removing local file $ZIP_FILE..."
rm -f "$ZIP_FILE"

echo "✅ Cleanup complete."