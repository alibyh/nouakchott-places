# Deploying Nouakchott Places Manager

## 🚀 Deploy to Render (Free & Easy)

### Step 1: Prepare for Deployment

1. Create a GitHub repository (if you haven't):
```bash
cd /Users/alibyh/Desktop/Projects/voiceApp/famous_places_nktt
git init
git add .
git commit -m "Initial commit: Nouakchott Places Manager"
```

2. Create a GitHub repo at https://github.com/new and push:
```bash
git remote add origin https://github.com/YOUR-USERNAME/nouakchott-places.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://render.com (create free account)
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name**: nouakchott-places
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. Click "Create Web Service"

**Your app will be live at**: `https://nouakchott-places.onrender.com`

✅ Access from phone, share with colleagues!

---

## 🌐 Alternative: Deploy to Railway (Also Free)

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Railway auto-detects Python and deploys

**Your app will be live at**: `https://YOUR-APP.railway.app`

---

## 📱 Quick Sharing: ngrok (Temporary Link)

For quick testing, share a temporary link:

```bash
# Install ngrok
brew install ngrok

# Run your app
python3 app.py

# In another terminal, create tunnel
ngrok http 5000
```

You'll get a URL like: `https://abc123.ngrok.io`
Share this with colleagues (valid for 2 hours on free plan).

---

## ⚡ Deploy to PythonAnywhere (Free Python Hosting)

1. Go to https://www.pythonanywhere.com
2. Create free account
3. Upload your files
4. Configure web app with Flask
5. Set working directory

**Your app will be at**: `https://YOUR-USERNAME.pythonanywhere.com`

---

## 🔐 Important: Add Authentication

Since this will be public, add basic password protection:

```python
# In app.py, add at the top
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    """Check if username/password is valid."""
    return username == 'admin' and password == 'YOUR-SECURE-PASSWORD'

def authenticate():
    """Send 401 response for authentication."""
    return Response(
        'Please login', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Protect all routes
@app.route('/')
@requires_auth
def index():
    return render_template('index.html')

@app.route('/api/places', methods=['GET'])
@requires_auth
def get_places():
    # ... rest of code
```

---

## 📊 Recommended Setup

**For you + colleagues (permanent access):**
→ Use **Render** or **Railway** (free, always online)

**For quick demo (temporary):**
→ Use **ngrok** (instant, 2-hour links)

**For Python-focused hosting:**
→ Use **PythonAnywhere** (free tier available)

---

## 🔒 Security Checklist

Before deploying:
- [ ] Add authentication (see above)
- [ ] Change default passwords
- [ ] Add rate limiting (optional)
- [ ] Backup nouakchott_places.json
- [ ] Set `debug=False` in app.py ✅ (already done)
- [ ] Add HTTPS (Render/Railway do this automatically)

---

## 📝 Environment Variables (for deployment)

Most platforms need these files (already created):
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - How to run the app
- ✅ `app.py` updated to use PORT environment variable

---

Choose your deployment method and follow the steps above!
