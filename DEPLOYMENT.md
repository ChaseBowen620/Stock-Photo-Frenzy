# Deploying Stock Photo Frenzy to Render

This guide will help you deploy the Stock Photo Frenzy game to Render.

## Prerequisites

- A Render account (sign up at https://render.com)
- A Shutterstock API access token
- A GitHub account (recommended) or ability to connect your repository

## Step-by-Step Deployment

### Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub**
   - Create a new repository on GitHub
   - Push your `stock-photo-frenzy` folder to the repository

2. **Create a new Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing `stock-photo-frenzy`

3. **Configure the service**
   - **Name**: `stock-photo-frenzy` (or any name you prefer)
   - **Root Directory**: `stock-photo-frenzy` (if your repo has multiple folders)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn src.app:app`
   - Render should automatically detect `render.yaml` if it's in the root

4. **Set Environment Variables**
   - In the Render dashboard, go to your service → Environment
   - Add the following:
     - `SECRET_KEY`: Generate a random string (or Render will auto-generate)
     - `SHUTTERSTOCK_ACCESS_TOKEN`: Your Shutterstock API token
     - `SHUTTERSTOCK_BASE_URL`: `https://api.shutterstock.com/v2`

5. **Create a PostgreSQL Database (Optional but Recommended)**
   - In Render dashboard, click "New +" → "PostgreSQL"
   - Name it: `stock-photo-frenzy-db`
   - Copy the **Internal Database URL**
   - Add it as an environment variable: `DATABASE_URL`
   - Note: If you don't create a database, it will use SQLite (not recommended for production)

6. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your app
   - Wait for the build to complete (usually 2-5 minutes)

7. **Access your app**
   - Your app will be available at: `https://your-app-name.onrender.com`
   - Render provides a free `.onrender.com` subdomain

### Option 2: Manual Configuration (Without render.yaml)

1. **Push your code to GitHub** (same as above)

2. **Create a new Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

3. **Configure the service manually:**
   - **Name**: `stock-photo-frenzy`
   - **Root Directory**: `stock-photo-frenzy` (if needed)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn src.app:app`
   - **Python Version**: `3.12.0` (or latest)

4. **Set Environment Variables** (same as Option 1)

5. **Create Database** (same as Option 1)

6. **Deploy** (same as Option 1)

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `SHUTTERSTOCK_ACCESS_TOKEN` | Your Shutterstock API token | Yes |
| `SHUTTERSTOCK_BASE_URL` | Shutterstock API base URL | No (defaults to v2) |
| `DATABASE_URL` | PostgreSQL connection string | No (uses SQLite if not set) |

## Important Notes

1. **Free Tier Limitations:**
   - Render's free tier spins down after 15 minutes of inactivity
   - First request after spin-down may take 30-60 seconds
   - Consider upgrading for production use

2. **Database:**
   - SQLite works for development but PostgreSQL is recommended for production
   - Render provides free PostgreSQL databases

3. **Static Files:**
   - Flask automatically serves static files from the `static/` folder
   - No additional configuration needed

4. **CORS (if needed):**
   - If you need to access the API from other domains, you may need to add CORS headers
   - Currently not needed for the game itself

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is in the root of your `stock-photo-frenzy` folder
- Verify Python version compatibility
- Check build logs in Render dashboard

### App Crashes on Start
- Verify all environment variables are set
- Check that `SHUTTERSTOCK_ACCESS_TOKEN` is valid
- Review logs in Render dashboard

### Database Issues
- Ensure `DATABASE_URL` is set correctly
- For PostgreSQL, use the Internal Database URL (not External)
- Check that database is created and accessible

### Images Not Loading
- Verify `SHUTTERSTOCK_ACCESS_TOKEN` is correct
- Check API quota/limits
- Review error logs for API response details

## Updating Your App

After making changes:
1. Push changes to your GitHub repository
2. Render will automatically detect and redeploy
3. Or manually trigger a deploy from the Render dashboard

## Custom Domain (Optional)

1. In Render dashboard, go to your service → Settings
2. Click "Add Custom Domain"
3. Follow the DNS configuration instructions
4. Render provides free SSL certificates

