# Google OAuth Setup Guide

## Step 1: Get Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the **Google+ API**:
   - Search for "Google+ API" in the search bar
   - Click Enable
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Choose **Web application**
6. Add authorized redirect URIs:
   - `http://localhost:8000/accounts/google/callback/` (for local development)
   - `https://your-domain.com/accounts/google/callback/` (for production)
7. Copy the **Client ID** and **Client Secret**

## Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/accounts/google/callback/
```

For production (Render/Vercel):
```env
GOOGLE_OAUTH_REDIRECT_URI=https://your-domain.com/accounts/google/callback/
```

## Step 3: Test Locally

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Go to `http://localhost:8000/login/`
3. Click "Continue with Google"
4. Sign in with your Google account
5. You should be redirected to the home page

## Step 4: Deploy

When deploying to Render/Vercel:

1. Add environment variables to your hosting platform:
   - `GOOGLE_OAUTH_CLIENT_ID`
   - `GOOGLE_OAUTH_CLIENT_SECRET`
   - `GOOGLE_OAUTH_REDIRECT_URI=https://your-deployed-domain.com/accounts/google/callback/`

2. Update your Google OAuth credentials in Google Cloud Console:
   - Add your production redirect URI: `https://your-deployed-domain.com/accounts/google/callback/`

## How It Works

- **Login Button**: Redirects to `/accounts/google/login/`
- **Google Consent**: User grants permission
- **Callback**: Google redirects to `/accounts/google/callback/` with auth code
- **Token Exchange**: Backend exchanges code for access token
- **User Creation**: Creates user if new, otherwise logs in existing user
- **Session**: User is logged in and redirected to the requested page

## Troubleshooting

### "Google OAuth not configured"
- Check that `GOOGLE_OAUTH_CLIENT_ID` is set in `.env`
- Restart the development server after changing `.env`

### "Invalid state token"
- Clear browser cookies and try again
- Make sure only one browser tab/window is open for the OAuth flow

### "Could not get email from Google"
- Ensure you're using a valid Google account
- Check that the Google+ API is enabled in Google Cloud Console

### Redirect URI mismatch error
- Ensure the redirect URI in `.env` exactly matches the one in Google Cloud Console
- Include the trailing slash: `/accounts/google/callback/`
- Use `http://` for local, `https://` for production
