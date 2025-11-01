# User Accounts Setup Guide

This guide explains how to set up and use the new passwordless authentication system in WildID.

## What Changed

### ✅ Added Features
- **Passwordless email authentication** - Users sign in via magic links sent to their email
- **User accounts** - Automatic account creation on first sign-in
- **History tracking** - All identifications are saved to user history (when signed in)
- **User dashboard** - View all past identifications in one place

### 🗑️ Removed Features
- **CAPTCHA system** - Removed custom CAPTCHA implementation
- **Rate limiting for non-members** - Simplified security approach

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `Flask-SQLAlchemy` - Database ORM
- `Flask-Mail` - Email sending
- `itsdangerous` - Token generation

### 2. Configure Environment Variables

Copy the example environment file and update it:

```bash
cp env.example .env
```

Update the following in your `.env` file:

```env
# Database (SQLite by default, can use PostgreSQL in production)
DATABASE_URL=sqlite:///wildid.db

# Email Configuration
# For DEVELOPMENT - use Mailhog (see below)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False

# For PRODUCTION - use a real email service
# Example with Gmail:
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password
# MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### 3. Set Up Email for Development

For development, we recommend using **Mailhog** to test email functionality without sending real emails:

```bash
# Using Docker
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Or install directly (requires Go)
go install github.com/mailhog/MailHog@latest
MailHog
```

Then access the Mailhog web interface at http://localhost:8025 to view sent emails.

**Note**: In development mode, magic links are also printed to the console for easy testing.

### 4. Initialize the Database

The database is automatically created when you first run the app:

```bash
python app.py
```

The SQLite database file (`wildid.db`) will be created in the project root.

### 5. Run the Application

```bash
python app.py
```

Visit http://localhost:3000

## How to Use

### For Users

1. **Sign In/Register**
   - Click "Sign In" in the navigation
   - Enter your email address
   - Check your email for the magic link
   - Click the link to sign in (valid for 15 minutes)

2. **Identify Animals**
   - Upload an animal photo on the Discovery page
   - View the identification results
   - If signed in, the identification is automatically saved to your history

3. **View History**
   - Click "History" in the navigation (only visible when signed in)
   - See all your past identifications with images
   - Filter by animal type, conservation status, etc.

4. **Sign Out**
   - Click "Sign Out" in the navigation

### For Developers

#### Database Models

**User Model** (`models.py`)
```python
- id: Primary key
- email: Unique email address
- created_at: Account creation timestamp
- last_login: Last login timestamp
- is_active: Account status
```

**Identification Model** (`models.py`)
```python
- id: Primary key
- user_id: Foreign key to User
- created_at: Identification timestamp
- species: Scientific name
- common_name: Common name
- animal_type: Type of animal
- conservation_status: Conservation status
- confidence: AI confidence level
- description: Description of the animal
- image_data: Base64 encoded image
- image_mime: Image MIME type
- result_json: Full AI result as JSON
```

**LoginToken Model** (`models.py`)
```python
- id: Primary key
- email: User email
- token: Unique token string
- created_at: Token creation timestamp
- expires_at: Token expiration (15 minutes)
- used: Whether token has been used
- used_at: When token was used
```

#### Authentication Flow

1. User enters email on `/auth/login`
2. System generates a secure token and saves to `LoginToken` table
3. Email with magic link is sent to user
4. User clicks link which goes to `/auth/verify?token=...`
5. System verifies token is valid and not expired
6. User is created (if new) or retrieved
7. User is logged in via session
8. Token is marked as used

#### API Endpoints

- `GET /` - Home page
- `GET /discovery` - Upload/identification page
- `GET /auth/login` - Login page
- `POST /auth/login` - Send magic link
- `GET /auth/verify` - Verify magic link token
- `GET /auth/logout` - Log out
- `GET /history` - User's identification history (requires auth)
- `POST /identify` - Upload and identify animal
- `GET /map` - Show habitat map
- `GET /api/habitat/<species>` - Get habitat data

## Production Deployment

### Email Configuration

For production, use a real email service:

**Gmail** (requires App Password):
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

**SendGrid**:
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

**AWS SES**:
```env
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-ses-smtp-username
MAIL_PASSWORD=your-ses-smtp-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

### Database

For production, consider using PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/wildid
```

### Security Considerations

1. **Use strong SECRET_KEY**: Generate with `python -c "import secrets; print(secrets.token_hex(32))"`
2. **Enable HTTPS**: Set `SESSION_COOKIE_SECURE=true`
3. **Secure database**: Use proper database credentials and network isolation
4. **Rate limiting**: Consider adding rate limiting to prevent abuse
5. **Email validation**: Current implementation has basic validation, consider more robust solutions
6. **Token cleanup**: Implement periodic cleanup of expired tokens

## Troubleshooting

### Emails not sending in development
- Make sure Mailhog is running: `docker ps` should show mailhog container
- Check Mailhog web interface at http://localhost:8025
- Check console output for printed magic links

### Database errors
- Delete `wildid.db` and restart the app to recreate tables
- Check file permissions on the database file
- Ensure SQLite is installed (should be included with Python)

### Magic links not working
- Check token hasn't expired (15 minute window)
- Ensure token hasn't been used already
- Check database for `login_tokens` entries

### Users not staying logged in
- Check `SESSION_TYPE` is set to `filesystem`
- Ensure `flask_session` directory exists and is writable
- Check browser allows cookies

## Future Enhancements

Potential features to add:
- Google reCAPTCHA for non-authenticated users
- OAuth providers (Google, GitHub, etc.)
- Profile management (avatar, bio, preferences)
- Social features (share identifications, comments)
- Advanced search and filtering in history
- Export history as CSV/PDF
- Email notifications for new features
- Two-factor authentication option
- Account deletion/data export (GDPR compliance)

## Support

For issues or questions, please check:
- Application logs in `app.log`
- Console output during development
- Database contents using SQLite browser
- Email service logs

