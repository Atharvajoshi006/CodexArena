# Google OAuth Credentials Setup - Complete Guide

## Step 1: Go to Google Cloud Console

1. Open https://console.cloud.google.com in your browser
2. Sign in with your Google account (create one if needed)

## Step 2: Create a New Project

1. Look at the top left - find the **Project Dropdown** (shows "My First Project" or similar)
2. Click on it
3. Click **"NEW PROJECT"**
4. Enter project name: `CodexArena` (or any name you prefer)
5. Click **"CREATE"**
6. Wait 30 seconds for the project to be created
7. Click the **Project Dropdown** again and select your `CodexArena` project

## Step 3: Enable Google+ API

1. In the left sidebar, click **"APIs & Services"**
2. Click **"Enable APIs and Services"** (big button in the center)
3. Search for **"Google+ API"**
4. Click on it
5. Click **"ENABLE"**
6. Wait for it to enable

## Step 4: Create OAuth 2.0 Credentials

1. In the left sidebar, click **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** button at the top
3. Select **"OAuth client ID"**
4. You'll see a popup: "To use OAuth 2.0 you must first set a consent screen"
5. Click **"CONFIGURE CONSENT SCREEN"**

## Step 5: Configure OAuth Consent Screen

1. Choose **"External"** user type
2. Click **"CREATE"**
3. Fill in the form:
   - **App name**: `CodexArena`
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click **"SAVE AND CONTINUE"** (skip optional sections)
5. Review and click **"BACK TO DASHBOARD"**

## Step 6: Create OAuth 2.0 Client ID

1. Click **"Credentials"** in the left sidebar
2. Click **"+ CREATE CREDENTIALS"** again
3. Select **"OAuth client ID"**
4. Choose **"Web application"**
5. Give it a name: `CodexArena Web`
6. Under **"Authorized redirect URIs"**, add BOTH:
   ```
   http://localhost:8000/google/callback/
   https://your-domain.com/google/callback/
   ```
   (Replace `your-domain.com` with your actual Render domain later)

7. Click **"CREATE"**
8. A popup appears with your credentials!

## Step 7: Copy Your Credentials

You'll see a popup or page with:
- **Client ID** (looks like: `123456789-abc123def456.apps.googleusercontent.com`)
- **Client Secret** (looks like: `GOCPK_AbCdEfGhIjKlMnOpQr...`)

**COPY BOTH OF THESE** (they're sensitive!)

## Step 8: Create `.env` File

In your project root (`c:\Users\athar\OneDrive\Desktop\Projects\CodexArena`), create a file named `.env`:

```env
DEBUG=True
SECRET_KEY=your-long-random-secret-here

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=paste-your-client-id-here
GOOGLE_OAUTH_CLIENT_SECRET=paste-your-client-secret-here
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/google/callback/
```

Replace:
- `paste-your-client-id-here` with your actual Client ID
- `paste-your-client-secret-here` with your actual Client Secret

## Step 9: Test Locally

1. Open a terminal and restart the dev server:
   ```bash
   python manage.py runserver 8000
   ```

2. Go to http://localhost:8000/login/

3. Click **"Continue with Google"**

4. You should now see Google's login screen!

5. Sign in with your Google account

6. You'll be redirected back to CodexArena and logged in!

## Step 10: For Production (Render)

When you deploy to Render:

1. Go to your Render dashboard
2. Open your backend service
3. Click **"Environment"** tab
4. Add these variables:
   ```
   GOOGLE_OAUTH_CLIENT_ID=paste-your-client-id-here
   GOOGLE_OAUTH_CLIENT_SECRET=paste-your-client-secret-here
   GOOGLE_OAUTH_REDIRECT_URI=https://your-render-domain.com/google/callback/
   ```

5. Also add this to Google Cloud Console:
   - Go to Credentials
   - Edit the OAuth Client
   - Add authorized redirect URI: `https://your-render-domain.com/google/callback/`

6. Deploy and test!

## Troubleshooting

### "Error: redirect_uri_mismatch"
- Make sure the redirect URI in your code matches EXACTLY in Google Cloud Console
- Check for trailing slash: `/google/callback/` (WITH slash)
- Use `http://` for local, `https://` for production

### "Error: The OAuth client was not found"
- The credentials aren't set in `.env`
- Check that `GOOGLE_OAUTH_CLIENT_ID` is in `.env`
- Restart the dev server after changing `.env`

### Nothing happens when I click the button
- Make sure `.env` has the correct credentials
- Check browser console for errors
- Make sure the button points to `/google/login/` (already fixed!)

## Important Security Notes

⚠️ **DO NOT commit `.env` to GitHub!**
- It's already in `.gitignore` ✓
- Never share your Client Secret

✓ Your credentials are safe:
- They're only used by your backend
- Never sent to the frontend
- The frontend only sees the Google redirect

## Need Help?

Check these files for reference:
- Backend logic: `accounts/views.py` (lines 118-214)
- Settings: `codexarena/settings.py` (bottom of file)
- Button: `templates/login.html` (line 338)
