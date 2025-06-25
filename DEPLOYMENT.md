# ImpactAI - Southern Impact Quote Assistant

## 🚀 Deployment Instructions

### Option 1: Render Deployment (Recommended)

1. **Database Setup:**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com)
   - Create free account and free cluster (M0 Sandbox)
   - Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/impactai`

2. **Deploy to Render:**
   - Push code to GitHub repository
   - Go to [Render.com](https://render.com)
   - Connect GitHub account
   - Create new "Web Service"
   - Select your repository
   - Choose "Backend" first:
     - Environment: Python
     - Build Command: `cd backend && pip install -r requirements.txt`
     - Start Command: `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`
     - Add environment variable: `MONGO_URL` (your MongoDB Atlas connection string)
   
3. **Deploy Frontend:**
   - Create another "Web Service"
   - Environment: Node
   - Build Command: `cd frontend && yarn install && yarn build`
   - Start Command: `cd frontend && npx serve -s build -p $PORT`
   - Add environment variable: `REACT_APP_BACKEND_URL` (your backend URL from step 2)

### Option 2: Vercel + Render

**Frontend (Vercel):**
- Connect GitHub to Vercel
- Set Root Directory: `frontend`
- Framework: React
- Build Command: `yarn build`
- Environment Variable: `REACT_APP_BACKEND_URL`

**Backend (Render):**
- Same as above backend setup

### Option 3: Railway (Alternative)

1. Go to [Railway.app](https://railway.app)
2. Connect GitHub
3. Deploy from repo
4. Set environment variables

## 🔧 Environment Variables Needed

**Backend:**
- `MONGO_URL`: Your MongoDB Atlas connection string

**Frontend:**
- `REACT_APP_BACKEND_URL`: Your backend URL (e.g., https://your-backend.onrender.com)

## 📝 Pre-Deployment Checklist

- [ ] Push code to GitHub
- [ ] Set up MongoDB Atlas database
- [ ] Update CORS origins in backend if needed
- [ ] Test environment variables
- [ ] Check build commands work locally

## 🌐 Custom Domain (Optional)

Both Render and Vercel support custom domains on free tier!

## 💡 Tips

- Use Render for both if you want simplicity
- Use Vercel + Render for potentially better performance
- Always use environment variables for sensitive data
- Enable automatic deployments from GitHub

## 🔒 Security Notes

- Never commit API keys or database URLs
- Use environment variables for all sensitive data
- Set up proper CORS origins
- Enable HTTPS (automatic on these platforms)