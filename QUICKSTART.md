# 🚀 Quick Start - User Accounts

## What's New?

Your WildID app now has **passwordless user accounts**! Users can sign in with just their email (no passwords needed) and their animal identifications are automatically saved to their personal history.

## Setup (5 minutes)

### 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Email (Development)

For testing, use Mailhog (it captures emails locally):

```bash
# Using Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

Then view emails at: http://localhost:8025

### 3. Update Environment Variables

Your `.env` file already has the basics, but add these if missing:

```env
# Database (auto-created)
DATABASE_URL=sqlite:///wildid.db

# Email (for magic links)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_DEFAULT_SENDER=noreply@wildid.app
```

### 4. Run the App

```bash
python app.py
```

The database will be created automatically on first run.

## How It Works

### For Users:

1. **Sign In**
   - Click "Sign In" → Enter email → Check inbox
   - Click magic link in email (or console in dev mode)
   - That's it! No password needed

2. **Identify Animals**
   - Upload photos as before
   - If signed in, identifications are auto-saved to history

3. **View History**
   - Click "History" to see all past identifications
   - Each entry shows the image, species, and details

### What Was Removed:

- ❌ Custom CAPTCHA system
- ❌ Rate limiting for non-members
- ❌ Manual security verification

All replaced with a cleaner, modern user account system!

## Testing

### Quick Test Flow:

1. Start the app: `python app.py`
2. Start Mailhog: `docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog`
3. Go to http://localhost:3000
4. Click "Sign In"
5. Enter any email (e.g., test@example.com)
6. Check console output for magic link OR visit http://localhost:8025
7. Click the magic link
8. You're signed in! Upload an image to test history tracking

### Console Output Example:

```
============================================================
🔗 MAGIC LINK FOR test@example.com
============================================================
http://localhost:3000/auth/verify?token=abc123...
============================================================
```

## Files Changed

### New Files:
- `models.py` - Database models (User, Identification, LoginToken)
- `auth.py` - Authentication manager (magic links, sessions)
- `templates/login.html` - Sign in page
- `templates/history.html` - User history page
- `SETUP_ACCOUNTS.md` - Detailed documentation

### Modified Files:
- `app.py` - Added auth routes, removed CAPTCHA, added history tracking
- `security.py` - Simplified (removed CAPTCHA code)
- `requirements.txt` - Added SQLAlchemy, Flask-Mail
- `templates/index.html` - Added sign in/out links
- `templates/discovery.html` - Removed CAPTCHA, added sign-in prompt
- `templates/results.html` - Added sign in/out links
- `env.example` - Added database and email config

## Production Deployment

For production, use a real email service:

**Gmail** (need App Password):
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

**SendGrid**:
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

See `SETUP_ACCOUNTS.md` for more details.

## Troubleshooting

**Emails not arriving?**
- Check Mailhog is running: http://localhost:8025
- Look for magic link in console output

**Database errors?**
- Delete `wildid.db` and restart (it will be recreated)

**Magic link expired?**
- Links expire after 15 minutes
- Request a new one

## Next Steps

Consider adding:
- Google reCAPTCHA for non-authenticated users (as you mentioned)
- Profile customization
- Social sharing features
- Export history as PDF/CSV

For detailed information, see `SETUP_ACCOUNTS.md`.

Enjoy your new user account system! 🎉


