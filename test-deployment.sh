#!/bin/bash
# Pre-deployment test script

echo "🧪 Testing ImpactAI Quote Assistant for Deployment..."

# Test Frontend Build
echo "📦 Testing frontend build..."
cd frontend
if yarn build; then
    echo "✅ Frontend build successful!"
    echo "📁 Build files created in frontend/build/"
else
    echo "❌ Frontend build failed!"
    exit 1
fi

cd ..

# Test Backend Dependencies
echo "🐍 Testing backend dependencies..."
cd backend
if pip install -r requirements.txt > /dev/null 2>&1; then
    echo "✅ Backend dependencies installed successfully!"
else
    echo "❌ Backend dependency installation failed!"
    exit 1
fi

cd ..

echo ""
echo "🎉 All tests passed! Ready for deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Get MongoDB Atlas connection string"
echo "2. Push code to GitHub"
echo "3. Deploy to your chosen platform"
echo "4. Set environment variables"
echo ""
echo "💡 Need help? Check DEPLOYMENT.md for detailed instructions!"