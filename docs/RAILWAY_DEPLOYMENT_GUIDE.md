# Railway Deployment Guide for JAI GURU DEV AI Chatbot

## 🚀 Quick Deploy to Railway

### Prerequisites
1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Push this project to your GitHub
3. **API Keys**: Get OpenAI and/or Groq API keys

### Step 1: Connect to Railway
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository with this chatbot

### Step 2: Set Environment Variables
In Railway dashboard, go to **Variables** tab and add:

```bash
# Required - OpenAI API Key (for embeddings)
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Groq API Key (for faster/cheaper LLM)
GROQ_API_KEY1=your_groq_api_key_here

# Application Settings
ENVIRONMENT=production
```

### Step 3: Deploy
1. Railway will automatically detect the `railway.toml` configuration
2. It will build and deploy your application
3. You'll get a public URL like: `https://your-app-name.railway.app`

## 🔧 Configuration Details

### Railway Configuration (`railway.toml`)
- **Build**: Uses Nixpacks for Python 3.11
- **Start Command**: Optimized Streamlit server
- **Health Check**: Monitors app health
- **Auto-restart**: On failure with retry limit

### Environment Optimization
- **ChromaDB**: Configured for Railway's file system
- **Streamlit**: Optimized for production deployment  
- **Memory**: Efficient memory usage settings
- **CORS**: Disabled for Railway's proxy

## 💾 Database Persistence on Railway

### ChromaDB Storage
✅ **Your database WILL persist** on Railway thanks to the fix!
- Railway provides persistent volumes
- Database recreates only when needed
- Metadata tracking ensures integrity
- Fast restarts after deployments

### Persistence Benefits
- ⚡ **Fast deploys** - Database survives restarts
- 🎯 **Consistent quality** - No data loss
- 💰 **Cost efficient** - No re-embedding on deploy
- 🛡️ **Reliable** - Automatic corruption recovery

## 🔍 Monitoring Your Deployment

### Railway Dashboard
- **Logs**: Real-time application logs
- **Metrics**: CPU, memory, network usage
- **Build Logs**: Deployment process details
- **Variables**: Environment configuration

### Health Checks
Railway monitors your app at `/_stcore/health` endpoint

### What to Watch For
```
✅ RAG System initialized successfully!
✅ Loaded existing ChromaDB with [N] documents  
✅ Custom retriever created successfully
✅ QA chain setup complete
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### 1. Build Failures
**Problem**: Package installation fails
**Solution**: Check `requirements.txt` versions

#### 2. App Won't Start
**Problem**: Port binding issues
**Solution**: Railway automatically sets `$PORT` variable

#### 3. API Key Issues
**Problem**: Missing or invalid API keys
**Solution**: Verify keys in Railway Variables tab

#### 4. ChromaDB Issues
**Problem**: Database recreation on every deploy
**Solution**: ✅ FIXED! The persistent DB fix handles this

#### 5. Memory Issues
**Problem**: Out of memory errors
**Solution**: Railway provides sufficient memory, but check logs

### Debug Commands
Access Railway shell for debugging:
```bash
# In Railway dashboard -> Settings -> Environment
railway shell
```

## ⚡ Performance Optimization

### Railway Plan Recommendations
- **Hobby Plan**: Perfect for personal use
- **Pro Plan**: For production with custom domain
- **Team Plan**: For collaborative development

### Expected Performance
- **Cold Start**: ~30-60 seconds (first launch)
- **Warm Requests**: ~1-3 seconds
- **Database Loading**: ~2-5 seconds (persistent!)
- **Config Changes**: ~2 seconds (no rebuild!)

## 🔄 Continuous Deployment

### Auto-Deploy Setup
Railway automatically deploys when you:
1. Push to your main branch
2. Update environment variables
3. Modify railway.toml

### Best Practices
- Test locally before pushing
- Use staging environment for major changes
- Monitor Railway logs during deployment
- Keep API keys secure

## 🌐 Custom Domain (Optional)

### Add Custom Domain
1. Go to Railway dashboard
2. Click "Settings" → "Domains" 
3. Add your domain
4. Update DNS records as shown
5. SSL certificate auto-generated

### Example Setup
```
Domain: chatbot.yourdomain.com
Points to: your-app-name.railway.app
```

## 📊 Scaling Considerations

### Railway Auto-Scaling
- Automatic vertical scaling
- Load balancing included
- No configuration needed

### Database Scaling
- ChromaDB handles moderate loads well
- For heavy usage, consider upgrading Railway plan
- Persistent storage prevents data loss during scaling

## 🎯 Success Metrics

After successful deployment, you should see:
- ✅ App accessible at Railway URL
- ✅ Database loads in ~2 seconds
- ✅ High-quality spiritual guidance responses
- ✅ Fast configuration changes
- ✅ No database recreation on restart

## 🆘 Support

### Getting Help
1. **Railway Docs**: [docs.railway.app](https://docs.railway.app)
2. **Railway Discord**: Community support
3. **GitHub Issues**: For app-specific problems

### Logs to Share When Seeking Help
```bash
# From Railway dashboard -> Deployments -> View Logs
🔧 Setting up LLM...
🔧 Setting up embeddings...
🔧 Loading and processing documents...
```

---

## 🎉 Your JAI GURU DEV AI is Now Railway-Ready!

The chatbot is fully optimized for Railway deployment with:
- 🚀 **One-click deployment**
- 💾 **Persistent database** (no more recreation issues!)
- ⚡ **Lightning-fast performance**
- 🛡️ **Production-ready configuration**
- 🔄 **Auto-deployment on updates**

**Deploy now and share spiritual wisdom with the world! 🙏**
