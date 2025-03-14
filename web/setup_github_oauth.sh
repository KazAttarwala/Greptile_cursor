#!/bin/bash

# Setup GitHub OAuth credentials for the changelog app

echo "Setting up GitHub OAuth credentials for the changelog app"
echo "--------------------------------------------------------"
echo ""
echo "You need to create a GitHub OAuth application at:"
echo "https://github.com/settings/developers"
echo ""
echo "When creating the application, use these settings:"
echo "- Application name: Changelog Generator"
echo "- Homepage URL: http://localhost:5001"
echo "- Authorization callback URL: http://localhost:5001/api/auth/callback"
echo ""
echo "After creating the application, enter the credentials below:"
echo ""

read -p "GitHub Client ID: " CLIENT_ID
read -p "GitHub Client Secret: " CLIENT_SECRET
read -p "Flask Secret Key (or press enter to generate one): " SECRET_KEY

if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 24)
    echo "Generated Flask Secret Key: $SECRET_KEY"
fi

# Create .env file
cat > ../.env << EOF
# GitHub OAuth credentials
GITHUB_CLIENT_ID=$CLIENT_ID
GITHUB_CLIENT_SECRET=$CLIENT_SECRET
FLASK_SECRET_KEY=$SECRET_KEY

# Other environment variables
FLASK_APP=web/app.py
FLASK_ENV=development
EOF

echo ""
echo "Credentials saved to ../.env"
echo ""
echo "Make sure you have installed the required dependencies:"
echo "pip install authlib flask-login flask-cors requests python-dotenv"
echo ""
echo "To start the application with GitHub OAuth:"
echo "1. Run 'source ../.env' to load the environment variables"
echo "2. Start the Flask app: 'python web/app.py'"
echo "3. Start the React frontend: 'cd web/frontend && npm start'"
echo ""
echo "Setup complete!" 