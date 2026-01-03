#!/bin/bash
set -e

echo "🚀 Setting up Publix Expansion Predictor on EC2..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
echo "📦 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git (if not already installed)
echo "📦 Installing Git..."
sudo yum install -y git

# Install AWS CLI (if not already installed)
echo "📦 Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    rm -rf aws awscliv2.zip
fi

# Create app directory
echo "📁 Creating application directory..."
mkdir -p /home/ec2-user/publix
cd /home/ec2-user/publix

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repository: git clone <your-repo-url> ."
echo "2. Create .env file with your environment variables"
echo "3. Run: docker-compose up -d"
echo ""
echo "Note: You may need to log out and back in for Docker group changes to take effect."

