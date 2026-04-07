#!/bin/bash
# Cleanup OIDC Resources created during Lab Sprint
# Removes IAM Roles and OIDC Providers

set -e

echo "🧹 Starting OIDC Lab Cleanup..."
read -p "Are you sure? This deletes IAM roles. (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Cleanup cancelled."
    exit 0
fi

# Detach Policy
echo "🗑️  Detaching policies from GitHubActions-CI-CD-Role..."
aws iam detach-role-policy --role-name GitHubActions-CI-CD-Role --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy/CI-CD-S3-Read 2>/dev/null || true

# Delete Role
echo "🗑️  Deleting Role..."
aws iam delete-role --role-name GitHubActions-CI-CD-Role 2>/dev/null || echo "Role not found."

# Delete OIDC Provider
echo "🗑️  Deleting OIDC Provider..."
OIDC_ARN=$(aws iam list-openid-connect-providers --query "OpenIDConnectProviderList[?contains(Arn, 'github')].Arn" --output text)
if [ -n "$OIDC_ARN" ]; then
    aws iam delete-openid-connect-provider --open-id-connect-provider-arn "$OIDC_ARN"
    echo "✅ OIDC Provider deleted."
else
    echo "⚠️  No GitHub OIDC Provider found."
fi

echo "🎉 Cleanup complete."
