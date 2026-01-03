#!/bin/bash
# Script to add your current IP to the RDS security group

SECURITY_GROUP_ID="sg-0b63fc6c0d1aeff0a"
REGION="us-east-1"

# Get your current public IP
MY_IP=$(curl -s https://checkip.amazonaws.com)
MY_IP_CIDR="${MY_IP}/32"

echo "Your current IP: $MY_IP"
echo "Adding $MY_IP_CIDR to security group $SECURITY_GROUP_ID..."

aws ec2 authorize-security-group-ingress \
    --group-id $SECURITY_GROUP_ID \
    --protocol tcp \
    --port 5432 \
    --cidr $MY_IP_CIDR \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "✅ Successfully added your IP to the security group!"
    echo "You should now be able to connect to the database."
else
    echo "⚠️  Failed to add IP. It may already be in the security group."
fi

