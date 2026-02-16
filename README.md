# PowerDealer - Multi-Tenant Business Management Platform

A lightweight, modern web application for managing multi-tenant business operations built with Django + Vue 3.

## Project Overview

**Business Requirements (BRS.txt):**
- Multi-tenant business management platform
- Business owners can sign up and register their business
- Business owners can log in to manage their operations

**Technical Stack:**
- **Backend:** Django 5.2 + Django REST Framework
- **Frontend:** Vue 3 + Pinia (state management) + Axios
- **Authentication:** JWT (JSON Web Tokens)
- **Database:** SQLite (development) PostgreSQL (Production)

## Project Structure

```
PDB/
├── powerdealer/                 # Django backend
│   ├── manage.py
│   ├── db.sqlite3
│   ├── src/                     # Main project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── trading/                 # App for business logic
│       ├── models.py            # Business and BusinessOwner models
│       ├── serializers.py       # API serializers
│       ├── views.py             # API views
│       ├── urls.py              # App routes
│       ├── admin.py             # Django admin
│       └── migrations/
│
├── powerdealer_f/               # Vue 3 frontend
│   ├── src/
│   │   ├── api/                 # API client and services
│   │   │   ├── client.js        # Axios instance & interceptors
│   │   │   └── auth.js          # Auth API methods
│   │   ├── stores/              # Pinia stores
│   │   │   ├── auth.js          # Auth store
│   │   │   └── business.js      # Business store
│   │   ├── views/               # Page components
│   │   │   ├── SignupView.vue
│   │   │   ├── LoginView.vue
│   │   │   └── DashboardView.vue
│   │   ├── components/          # Reusable components
│   │   ├── App.vue              # Root component
│   │   ├── main.js              # Entry point
│   │   └── router.js            # Vue Router config
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
│
├── requirements.txt             # Python dependencies
├── guideline.txt                # Technical guidelines
└── BRS.txt                       # Business requirements
```

## API Endpoints

### Authentication
- `POST /api/auth/signup/` - Register new business owner
- `POST /api/auth/login/` - Login business owner
- `POST /api/token/refresh/` - Refresh JWT token

### Business Management
- `GET /api/business/` - Get current business details
- `PUT /api/business/` - Update business information

## Backend Setup

### Prerequisites
- Python 3.9+
- pip

### Installation

1. Navigate to backend directory:
```bash
cd powerdealer
```

2. Install dependencies:
```bash
pip install -r ../requirements.txt
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser (optional for admin access):
```bash
python manage.py createsuperuser
```

5. Start development server:
```bash
python manage.py runserver
```

Backend will run at: `http://localhost:8000`

## Frontend Setup

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

1. Navigate to frontend directory:
```bash
cd powerdealer_f
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will run at: `http://localhost:5173`

## Key Features

### 1. User Signup
- Create business owner account
- Register business details
- Automatic login after signup
- Returns JWT tokens for authentication

### 2. User Login
- Login with username and password
- Receive JWT tokens
- Automatic session restoration

### 3. Business Dashboard
- View business information
- Edit business details (name, email, phone, address, description)
- Real-time update reflection
- Logout functionality

### 4. Authentication System
- JWT-based authentication
- Token refresh mechanism
- Automatic token injection in API headers
- 401 error handling with token refresh

## Database Models

### Business
- `owner` - OneToOne relationship with Django User
- `name` - Business name (unique)
- `email` - Business email (unique)
- `phone` - Business phone
- `description` - Business description
- `address` - Business address
- `created_at` - Timestamp
- `updated_at` - Timestamp

## Development Guidelines

Following the lightweight software guideline:

### Backend
- ✅ Flat structure (all models in trading app)
- ✅ Simple serializers using ModelSerializer
- ✅ APIView for views
- ✅ Minimal validation
- ✅ No service layers unless needed

### Frontend
- ✅ Single axios instance in api/client.js
- ✅ Pinia stores for state management
- ✅ Flat folder structure
- ✅ Simple JWT auth (no complex refresh logic initially)
- ✅ Minimal testing

## Testing the Application

### 1. Start both servers
```bash
# Terminal 1 - Backend
cd powerdealer
python manage.py runserver

# Terminal 2 - Frontend
cd powerdealer_f
npm run dev
```

### 2. Register a Business Owner
- Go to `http://localhost:5173/signup`
- Fill in all required fields
- Click "Sign Up"

### 3. View Dashboard
- Automatically redirected to dashboard after signup
- View business information
- Edit and save changes

### 4. Logout and Login
- Click "Logout" button
- Go to login page
- Login with credentials
- View dashboard again

## Admin Panel

Access Django admin at: `http://localhost:8000/admin`

Log in with superuser credentials and manage:
- Users
- Businesses
- View all registrations

## Next Steps / Future Features

1. **Additional Business Operations**
   - Inventory management
   - Sales/transactions
   - Reports and analytics

2. **API Enhancements**
   - List all businesses (admin only)
   - Business statistics
   - Activity logging

3. **Frontend Improvements**
   - Better error handling UI
   - Loading states
   - Success notifications
   - Responsive design improvements

4. **Testing**
   - Unit tests for models
   - API endpoint tests
   - Component tests for Vue

5. **Deployment**
   - Production settings
   - Environment variables
   - Database migrations backup

## Troubleshooting

### CORS Errors
- Ensure backend CORS settings include frontend URL
- Check settings.py CORS_ALLOWED_ORIGINS

### 401 Unauthorized
- Token may have expired
- Clear localStorage and login again
- Check if token is being sent in Authorization header

### API Connection Issues
- Verify backend server is running on port 8000
- Check baseURL in api/client.js
- Verify no firewall issues

## Development Notes

- The application follows the lightweight software guideline for MVPs
- Focus on speed and simplicity over over-engineering
- Database uses SQLite for development (change to PostgreSQL for production)
- JWT tokens stored in localStorage (consider alternatives for production)

## License

Internal Development
