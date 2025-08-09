# 🚂 Railway Deploy Instructions - Athletic Emotion

## Project Information
- **Project Name:** athletic-emotion  
- **Project ID:** `daa4ac63-d597-4ba7-b10e-1baf84cbacad`
- **Repository:** https://github.com/danilapryadko/Odoo_SportsPit_Project
- **Token:** `e2a89410-8aeb-419c-8020-741fba8f9bf9`

## 🚀 Quick Deploy via Railway Dashboard

### Step 1: Open Railway Project
https://railway.app/project/daa4ac63-d597-4ba7-b10e-1baf84cbacad

### Step 2: Connect GitHub
1. Go to **Settings** → **Service** 
2. Click **Connect GitHub**
3. Select repository: `danilapryadko/Odoo_SportsPit_Project`
4. Branch: `main`

### Step 3: Add PostgreSQL
1. Click **New Service**
2. Select **Database** → **PostgreSQL**
3. Railway will automatically connect it to Odoo

### Step 4: Set Environment Variables
Add these in the Railway Dashboard → Variables:

```env
PORT=8069
ADMIN_PASSWORD=SportsPit2025!
WORKERS=2
LANG=ru_RU.UTF-8
TZ=Europe/Moscow
LOG_LEVEL=info
LIMIT_MEMORY_HARD=2684354560
LIMIT_MEMORY_SOFT=2147483648
```

### Step 5: Deploy
Railway will automatically deploy when you push to GitHub main branch.

## 🖥️ Deploy via CLI

```bash
# 1. Login to Railway
railway login

# 2. Link to project
railway link -p daa4ac63-d597-4ba7-b10e-1baf84cbacad

# 3. Deploy
railway up

# 4. Get URL
railway domain
```

## 📊 Monitoring

### View Logs
```bash
railway logs -f
```

### Check Status
```bash
railway status
```

### Open Dashboard
```bash
railway open
```

## 🔐 Access Credentials

- **URL:** Will be generated after deploy (format: `*.up.railway.app`)
- **Admin Login:** admin
- **Admin Password:** SportsPit2025!
- **Database:** PostgreSQL (auto-configured by Railway)

## ⏱️ Expected Timeline

1. **Build:** 3-5 minutes
2. **Database Init:** 1-2 minutes  
3. **Odoo Start:** 2-3 minutes
4. **Total:** ~10 minutes

## 🆘 Troubleshooting

### If deploy fails:
1. Check logs: `railway logs`
2. Verify environment variables
3. Ensure PostgreSQL is running
4. Check Dockerfile syntax

### If Odoo doesn't start:
1. Check DATABASE_URL is set
2. Verify ADMIN_PASSWORD is set
3. Check memory limits
4. Review odoo.conf settings

## 📝 Post-Deploy Steps

1. **Access Odoo:**
   - Open the generated URL
   - Login with admin credentials

2. **Initialize Database:**
   - Odoo will auto-create database on first run
   - Select Russian language
   - Set timezone to Europe/Moscow

3. **Install Modules:**
   - Manufacturing (MRP)
   - Inventory
   - Sales
   - Purchase
   - Quality Control

4. **Configure Company:**
   - Name: ООО "СпортПит"
   - Country: Russia
   - Currency: RUB

## 🔗 Useful Links

- **Railway Dashboard:** https://railway.app/project/daa4ac63-d597-4ba7-b10e-1baf84cbacad
- **GitHub Repo:** https://github.com/danilapryadko/Odoo_SportsPit_Project
- **Railway Docs:** https://docs.railway.app
- **Odoo Docs:** https://www.odoo.com/documentation/17.0/

---

**Ready to Deploy!** 🚀  
Project configured and waiting for deployment to athletic-emotion.