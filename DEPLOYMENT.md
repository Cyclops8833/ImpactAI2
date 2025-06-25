# ImpactAI - Southern Impact Quote Assistant

## 🚀 Free Deployment Options

### 🎯 Option 1: Render (Recommended - Simplest)

**Pros:** Free tier, full-stack support, automatic deployments, custom domains
**Cons:** Cold starts after inactivity

**Steps:**
1. **Database Setup:**
   - Go to [MongoDB Atlas](https://cloud.mongodb.com)
   - Create free account → Create cluster (M0 Sandbox - FREE)
   - Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/impactai`

2. **Deploy Backend:**
   - Push code to GitHub
   - Go to [Render.com](https://render.com) → "New Web Service"
   - Connect GitHub → Select repository
   - Settings:
     - **Environment:** Python
     - **Build Command:** `cd backend && pip install -r requirements.txt`
     - **Start Command:** `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`
     - **Environment Variables:**
       - `MONGO_URL`: (your MongoDB Atlas string)
       - `ALLOWED_ORIGINS`: `https://your-frontend-url.onrender.com`

3. **Deploy Frontend:**
   - Create another "Web Service"
   - Settings:
     - **Environment:** Node
     - **Build Command:** `cd frontend && yarn install && yarn build`
     - **Start Command:** `cd frontend && npx serve -s build -p $PORT`
     - **Environment Variables:**
       - `REACT_APP_BACKEND_URL`: `https://your-backend-url.onrender.com`

### 🎯 Option 2: Vercel + Railway

**Frontend (Vercel - FREE):**
- Go to [Vercel.com](https://vercel.com)
- Import from GitHub
- Root Directory: `frontend`
- Framework: React
- Environment Variable: `REACT_APP_BACKEND_URL`

**Backend (Railway - FREE):**
- Go to [Railway.app](https://railway.app)
- Deploy from GitHub
- Add MongoDB URL in variables

### 🎯 Option 3: Netlify + Render

**Frontend (Netlify):**
- Drag & drop build folder OR connect GitHub
- Build command: `cd frontend && yarn build`
- Publish directory: `frontend/build`

### 🎯 Option 4: All-in-One Alternatives

**Railway:** Full-stack deployment with database
**Cyclic:** Serverless deployment
**Deta:** Free forever tier

## 🔧 Required Environment Variables

### Backend (.env):
```bash
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/impactai
ALLOWED_ORIGINS=https://your-frontend-domain.com
PORT=8001
```

### Frontend (.env):
```bash
REACT_APP_BACKEND_URL=https://your-backend-domain.com
```

## 📋 Pre-Deployment Checklist

- [ ] Create MongoDB Atlas account & cluster
- [ ] Push code to GitHub
- [ ] Test build commands locally:
  - Frontend: `cd frontend && yarn build`
  - Backend: `cd backend && pip install -r requirements.txt`
- [ ] Get MongoDB connection string
- [ ] Choose deployment platform

## 🚀 Quick Start Commands

**Test Frontend Build:**
```bash
cd frontend
yarn install
yarn build
npx serve -s build
```

**Test Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload
```

## 🌐 Free Custom Domains

- **Render:** Custom domains on free tier
- **Vercel:** yourapp.vercel.app (custom domains available)
- **Netlify:** yourapp.netlify.app (custom domains available)

## 💡 Pro Tips

1. **Database:** Always use MongoDB Atlas free tier (512MB)
2. **Images:** Use CDN for any images (Cloudinary free tier)
3. **Monitoring:** Set up Render/Vercel notifications
4. **Backup:** Export database regularly
5. **Security:** Use environment variables for ALL sensitive data

## 🔒 Security Checklist

- [ ] MongoDB user has minimal required permissions
- [ ] CORS properly configured
- [ ] No hardcoded secrets in code
- [ ] Environment variables set correctly
- [ ] HTTPS enabled (automatic on these platforms)

## 📞 Need Help?

Common issues:
- **Build fails:** Check Node.js/Python versions
- **Database connection:** Verify MongoDB Atlas whitelist (0.0.0.0/0 for global access)
- **CORS errors:** Check ALLOWED_ORIGINS environment variable
- **Frontend can't reach backend:** Verify REACT_APP_BACKEND_URL

---

**Ready to deploy?** Get your MongoDB Atlas connection string and I'll help you with the final setup! 🚀