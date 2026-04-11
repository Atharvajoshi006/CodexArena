#!/usr/bin/env python
"""Validate Google OAuth setup"""
import os
import sys
from pathlib import Path

def check_setup():
    print("\n" + "="*70)
    print("GOOGLE OAUTH SETUP VERIFICATION")
    print("="*70)
    
    errors = []
    warnings = []
    
    # Check 1: .env file exists
    print("\n[1] Checking .env file...")
    env_path = Path(".env")
    if env_path.exists():
        print("    ✓ .env file exists")
    else:
        print("    ✗ .env file NOT FOUND")
        errors.append(".env file not found - create it with your credentials")
    
    # Check 2: Django setup
    print("\n[2] Setting up Django...")
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codexarena.settings')
        import django
        django.setup()
        print("    ✓ Django configured")
    except Exception as e:
        print(f"    ✗ Django setup failed: {e}")
        errors.append(str(e))
        return errors, warnings
    
    # Check 3: Check settings
    print("\n[3] Checking OAuth settings...")
    from django.conf import settings
    
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
    
    if client_id:
        if client_id == "":
            print("    ✗ GOOGLE_OAUTH_CLIENT_ID is empty")
            errors.append("Set GOOGLE_OAUTH_CLIENT_ID in .env")
        else:
            print(f"    ✓ Client ID configured: {client_id[:30]}...")
    else:
        print("    ✗ GOOGLE_OAUTH_CLIENT_ID not set")
        errors.append("Set GOOGLE_OAUTH_CLIENT_ID in .env")
    
    if client_secret:
        if client_secret == "":
            print("    ✗ GOOGLE_OAUTH_CLIENT_SECRET is empty")
            errors.append("Set GOOGLE_OAUTH_CLIENT_SECRET in .env")
        else:
            print(f"    ✓ Client Secret configured: {client_secret[:20]}...")
    else:
        print("    ✗ GOOGLE_OAUTH_CLIENT_SECRET not set")
        errors.append("Set GOOGLE_OAUTH_CLIENT_SECRET in .env")
    
    if redirect_uri:
        print(f"    ✓ Redirect URI: {redirect_uri}")
    else:
        print("    ✗ GOOGLE_OAUTH_REDIRECT_URI not set")
        errors.append("Set GOOGLE_OAUTH_REDIRECT_URI in .env")
    
    # Check 4: URL routing
    print("\n[4] Checking URL routes...")
    try:
        from accounts.urls import urlpatterns
        routes = [str(p.pattern) for p in urlpatterns]
        if any('google' in str(route) for route in routes):
            print("    ✓ Google OAuth routes registered")
        else:
            print("    ✗ Google OAuth routes NOT found")
            errors.append("Google OAuth routes not in URLs")
    except Exception as e:
        print(f"    ⚠ Could not verify routes: {e}")
    
    # Check 5: Views
    print("\n[5] Checking OAuth views...")
    try:
        from accounts.views import google_login, google_callback
        print("    ✓ Google OAuth views found")
    except ImportError as e:
        print(f"    ✗ Views not found: {e}")
        errors.append("Views not properly imported")
    
    # Summary
    print("\n" + "="*70)
    if errors:
        print("❌ SETUP INCOMPLETE - ERRORS FOUND:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
        print("\nFix these errors and run this script again.")
        return errors, warnings
    elif warnings:
        print("⚠️  SETUP READY WITH WARNINGS:")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    else:
        print("✅ SETUP COMPLETE - READY TO TEST!")
        print("\nNext steps:")
        print("  1. Start dev server: python manage.py runserver 8000")
        print("  2. Go to http://localhost:8000/login/")
        print("  3. Click 'Continue with Google'")
        print("  4. Sign in with your Google account")
        print("  5. You should be logged in!")
    
    print("="*70 + "\n")
    return errors, warnings

if __name__ == '__main__':
    errors, warnings = check_setup()
    sys.exit(1 if errors else 0)
