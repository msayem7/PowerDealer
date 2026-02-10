# Quick Setup Guide

## 1. Backend Setup (Django)

```bash
# Navigate to project root
cd "c:\My Files\Sayem\MySoft\Miru\PDB"

# Install dependencies
pip install -r requirements.txt

# Navigate to Django project
cd powerdealer

# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Optional: Create admin user
python manage.py createsuperuser

# Start the server
python manage.py runserver
```

**Backend will be available at:** `http://localhost:8000`

## 2. Frontend Setup (Vue 3)

```bash
# Navigate to frontend directory
cd "c:\My Files\Sayem\MySoft\Miru\PDB\powerdealer_f"

# Install dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be available at:** `http://localhost:5173`

## 3. API Endpoints

### Authentication
```
POST   /api/auth/signup/          Register new business owner
POST   /api/auth/login/           Login business owner
POST   /api/token/refresh/        Refresh JWT token
```

### Business Operations
```
GET    /api/business/             Get business details
PUT    /api/business/             Update business details
```

## 4. Test User Flow

### Signup (Frontend)
1. Go to `http://localhost:5173/signup`
2. Fill in:
   - Username
   - Email
   - Password
   - Business Name
   - Business Email
   - Phone (optional)
   - Description (optional)
3. Click "Sign Up"

### Dashboard
- You'll be redirected to dashboard
- View and edit business information
- Click "Logout" to exit

### Login
1. Go to `http://localhost:5173/login`
2. Enter username and password
3. Access dashboard

## 5. Admin Panel

Access at `http://localhost:8000/admin`

Manage:
- Users
- Businesses
- View all system data

## 6. Database

- Default: SQLite (powerdealer/db.sqlite3)
- Models: Business (linked to Django User)

## 7. Key Files

- **Backend Settings:** `powerdealer/src/settings.py`
- **Backend Routes:** `powerdealer/src/urls.py`
- **Business Model:** `powerdealer/trading/models.py`
- **Frontend Router:** `powerdealer_f/src/router.js`
- **Frontend Stores:** `powerdealer_f/src/stores/`
- **API Client:** `powerdealer_f/src/api/client.js`

## 8. Required Configuration

### Backend (settings.py)
- ✅ REST_FRAMEWORK with JWT authentication
- ✅ CORS headers configured
- ✅ Simple JWT settings (24hr access, 7days refresh)

### Frontend (vite.config.js)
- ✅ Port 5173
- ✅ Vue 3 plugin enabled

## 9. Troubleshooting

### Python/Django Issues
- Ensure Python 3.9+ installed
- Check all dependencies installed: `pip list`
- Try: `python -m pip install --upgrade pip`

### Node/Frontend Issues
- Ensure Node 16+ installed
- Clear node_modules: `rm -r node_modules`
- Reinstall: `npm install`

### CORS/API Issues
- Verify backend running on port 8000
- Check firewall allowing 8000 and 5173
- Verify CORS_ALLOWED_ORIGINS in settings.py

### Database Issues
- Delete db.sqlite3 to start fresh
- Re-run migrations: `python manage.py migrate`

## 10. Next Development Steps

1. Add more business models (products, customers, etc.)
2. Create additional API views and serializers
3. Build frontend pages for other operations
4. Add form validation and error messages
5. Implement notifications/toasts
6. Add unit and integration tests
7. Setup production deployment

## Commands Reference

### Backend
```bash
# Start server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Access admin
http://localhost:8000/admin

# Create migrations
python manage.py makemigrations

# Run migrations
python manage.py migrate
```

### Frontend
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Success Indicators

✅ Backend starts without errors
✅ Frontend loads on localhost:5173
✅ Can sign up new business
✅ Can login and access dashboard
✅ Can edit business information
✅ Can logout and login again
✅ Admin panel accessible

---

**Ready to start development!**
