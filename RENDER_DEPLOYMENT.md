# Render Deployment Guide

This guide will help you deploy your RCM SaaS Application to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your Firebase project credentials
3. Your application code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Environment Variables Setup

In your Render dashboard, set the following environment variables:

#### Required Variables:
```
FLASK_ENV=production
PORT=10000
SECRET_KEY=<generate-a-secure-secret-key>
JWT_SECRET_KEY=<generate-a-secure-jwt-secret-key>
FIREBASE_PROJECT_ID=mv20-a1a09
FIREBASE_STORAGE_BUCKET=gs://mv20-a1a09.firebasestorage.app
DATABASE_URL=https://mv20-a1a09-default-rtdb.firebaseio.com/
```

#### Optional Variables:
```
CORS_ORIGINS=https://your-frontend-domain.com
LOG_LEVEL=INFO
RATELIMIT_DEFAULT=1000 per hour
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
```

### 2. Firebase Service Account

1. Download your Firebase service account key file (`ServiceAccountKey.json`)
2. In Render, go to your service settings
3. Add the service account key as an environment variable named `FIREBASE_SERVICE_ACCOUNT_KEY`
4. Copy the entire JSON content as the value (make sure to include all the curly braces and quotes)
5. Example format:
   ```json
   {"type":"service_account","project_id":"mv20-a1a09","private_key_id":"...","private_key":"...","client_email":"...","client_id":"...","auth_uri":"...","token_uri":"...","auth_provider_x509_cert_url":"...","client_x509_cert_url":"..."}
   ```

### 3. Deploy to Render

#### Option A: Using render.yaml (Recommended)
1. Push your code with the `render.yaml` file to your repository
2. In Render dashboard, click "New +" → "Web Service"
3. Connect your repository
4. Render will automatically detect the `render.yaml` configuration
5. Click "Create Web Service"

#### Option B: Manual Configuration
1. In Render dashboard, click "New +" → "Web Service"
2. Connect your repository
3. Configure the service:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app.main:app`
   - **Environment**: Python 3
   - **Plan**: Free (or upgrade as needed)

### 4. Health Check Configuration

The application includes a health check endpoint at `/health` that Render can use for monitoring.

### 5. Custom Domain (Optional)

1. In your Render service settings, go to "Custom Domains"
2. Add your domain
3. Follow the DNS configuration instructions

## Post-Deployment

### 1. Test Your Deployment
- Visit your Render URL
- Check the health endpoint: `https://your-app.onrender.com/health`
- Test your API endpoints

### 2. Monitor Logs
- Use Render's log viewer to monitor application logs
- Set up alerts for errors

### 3. Database Setup
- Ensure your Firebase project is properly configured
- Test database connectivity

## Troubleshooting

### Common Issues:

1. **Build Failures**
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version compatibility

2. **Runtime Errors**
   - Check environment variables are set correctly
   - Verify Firebase credentials

3. **CORS Issues**
   - Update `CORS_ORIGINS` with your frontend domain
   - Ensure HTTPS is used in production

4. **Memory Issues**
   - Consider upgrading to a paid plan
   - Optimize your application code

### Support
- Check Render's documentation: https://render.com/docs
- Review application logs in Render dashboard
- Test locally with production environment variables

## Security Notes

1. **Never commit sensitive data** like API keys or passwords
2. **Use environment variables** for all configuration
3. **Enable HTTPS** for production
4. **Regularly rotate** secret keys
5. **Monitor access logs** for suspicious activity
