# RCM SaaS Application

A scalable Revenue Cycle Management (RCM) SaaS platform designed specifically for Indian hospitals. This application provides comprehensive patient management, preauthorization management, and business intelligence capabilities.

## 🏥 Features

### Core Features
- **Patient Management**: Complete patient lifecycle management with medical history, insurance information, and document management
- **Preauth Management**: Streamlined preauthorization request processing with workflow automation
- **Preauth Process Management**: Advanced workflow management with state tracking and SLA monitoring
- **Business Intelligence Dashboards**: Comprehensive analytics and reporting for revenue cycle insights

### Key Capabilities
- Multi-tenant architecture supporting multiple hospitals
- Role-based access control with granular permissions
- Real-time notifications and alerts
- Document management with secure storage
- Audit logging and compliance tracking
- RESTful API with comprehensive documentation
- Scalable microservices architecture

## 🛠️ Tech Stack

- **Backend**: Python 3.9+, Flask 2.3.3
- **Database**: Google Firestore (NoSQL)
- **Storage**: Firebase Storage
- **Authentication**: JWT-based authentication
- **API**: RESTful API with Flask-RESTX
- **Documentation**: Swagger/OpenAPI 3.0
- **Testing**: pytest, pytest-flask
- **Code Quality**: black, flake8, isort

## 📁 Project Structure

```
app/
├── api/                          # API layer
│   └── v1/                       # API version 1
│       ├── routes/               # API routes
│       ├── controllers/          # Business logic controllers
│       └── middleware/           # Authentication, validation, error handling
├── config/                       # Configuration management
│   ├── firebase_config.py        # Firebase configuration
│   ├── app_config.py             # Application configuration
│   └── database_config.py        # Database configuration
├── core/                         # Core business logic
│   ├── models/                   # Database models
│   ├── services/                 # Business services
│   └── utils/                    # Core utilities
├── database/                     # Database layer
│   ├── firebase_client.py        # Firebase client
│   ├── firestore_client.py       # Firestore client
│   └── models/                   # Data models
├── features/                     # Feature modules
│   ├── patient_management/       # Patient management features
│   ├── preauth_management/       # Preauth management features
│   ├── preauth_process/          # Process management features
│   └── bi_dashboard/             # Business intelligence features
├── utils/                        # Utility functions
│   ├── validators.py             # Data validation utilities
│   ├── helpers.py                # Helper functions
│   ├── formatters.py             # Data formatting utilities
│   ├── encryption.py             # Encryption utilities
│   ├── email_utils.py            # Email utilities
│   └── file_utils.py             # File handling utilities
├── tests/                        # Test suite
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── docs/                         # Documentation
├── scripts/                      # Deployment and utility scripts
└── deployment/                   # Deployment configurations
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Cloud Platform account
- Firebase project setup
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rcm-saas-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Configure Firebase**
   - Place your `ServiceAccountKey.json` in the root directory
   - Update Firebase configuration in `app/config/firebase_config.py`

6. **Run the application**
   ```bash
   python app/main.py
   ```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Firebase Configuration
FIREBASE_PROJECT_ID=mv20-a1a09
FIREBASE_STORAGE_BUCKET=gs://mv20-a1a09.firebasestorage.app

# Database Configuration
FIRESTORE_DATABASE_ID=(default)

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Redis Configuration (for caching and rate limiting)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

### Firebase Setup

1. Create a Firebase project in the Google Cloud Console
2. Enable Firestore Database
3. Enable Firebase Storage
4. Generate a service account key
5. Download the JSON key file and place it as `ServiceAccountKey.json` in the root directory

## 📚 API Documentation

### Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Base URL

```
http://localhost:5000/api/v1
```

### Key Endpoints

#### Patient Management
- `GET /patients` - Get all patients
- `POST /patients` - Create new patient
- `GET /patients/{id}` - Get patient by ID
- `PUT /patients/{id}` - Update patient
- `DELETE /patients/{id}` - Delete patient

#### Preauth Management
- `GET /preauth` - Get all preauth requests
- `POST /preauth` - Create new preauth request
- `GET /preauth/{id}` - Get preauth request by ID
- `PUT /preauth/{id}` - Update preauth request
- `POST /preauth/{id}/submit` - Submit preauth request
- `POST /preauth/{id}/approve` - Approve preauth request
- `POST /preauth/{id}/reject` - Reject preauth request

#### Dashboard & Analytics
- `GET /dashboard/overview` - Get dashboard overview
- `GET /dashboard/preauth-analytics` - Get preauth analytics
- `GET /dashboard/revenue-analytics` - Get revenue analytics
- `GET /dashboard/patient-analytics` - Get patient analytics

For complete API documentation, visit `http://localhost:5000/api/docs` when the application is running.

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/unit/test_patient_management.py

# Run with verbose output
pytest -v
```

### Test Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for API endpoints
- `tests/fixtures/` - Test fixtures and mock data

## 🚀 Deployment

### Production Deployment

1. **Set up production environment**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   ```

2. **Install production dependencies**
   ```bash
   pip install gunicorn
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app.main:app
   ```

### Docker Deployment

1. **Build Docker image**
   ```bash
   docker build -t rcm-saas-app .
   ```

2. **Run container**
   ```bash
   docker run -p 5000:5000 rcm-saas-app
   ```

### Cloud Deployment

The application is designed to be deployed on:
- Google Cloud Platform (recommended)
- AWS
- Azure
- Heroku

## 📊 Monitoring and Logging

### Logging

The application includes comprehensive logging:
- Request/response logging
- Error logging
- Audit logging
- Performance metrics

### Health Checks

- Health endpoint: `GET /health`
- Database health: `GET /health/database`
- Storage health: `GET /health/storage`

## 🔒 Security

### Security Features

- JWT-based authentication
- Role-based access control
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting
- Audit logging

### Best Practices

- Use HTTPS in production
- Regularly rotate secrets
- Monitor access logs
- Keep dependencies updated
- Implement proper error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use meaningful commit messages
- Ensure all tests pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Version History

- **v1.0.0** - Initial release with core features
  - Patient management
  - Preauth management
  - Basic dashboard
  - API endpoints

## 🎯 Roadmap

### Upcoming Features
- [ ] Advanced analytics and reporting
- [ ] Mobile application
- [ ] Third-party integrations
- [ ] Advanced workflow automation
- [ ] Machine learning insights
- [ ] Multi-language support

---

**Built with ❤️ for Indian Healthcare**
