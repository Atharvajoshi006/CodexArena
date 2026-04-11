#!/bin/bash
# CodexArena Team Feature - deployment script
# Run this script to deploy the team recruitment feature

echo "=== CodexArena Team Feature Deployment ==="
echo ""

# Step 1: Create migrations
echo "[1/3] Creating database migrations..."
python manage.py makemigrations accounts
if [ $? -ne 0 ]; then
  echo "❌ Migration creation failed"
  exit 1
fi
echo "✓ Migrations created"
echo ""

# Step 2: Apply migrations
echo "[2/3] Applying database migrations..."
python manage.py migrate accounts
if [ $? -ne 0 ]; then
  echo "❌ Migration application failed"
  exit 1
fi
echo "✓ Database updated"
echo ""

# Step 3: Collect static files (if in production)
echo "[3/3] Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"
echo ""

echo "=== ✓ Deployment Complete ==="
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:8000/teams/ to view the teams page"
echo "  2. Login to create a team and test functionality"
echo "  3. Visit /admin/ to manage teams in the admin interface"
echo "  4. Check TEAM_FEATURE_SETUP.md for detailed documentation"
