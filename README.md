# VocaBloom Backend 🌱

A powerful Django REST API backend for the VocaBloom vocabulary learning application. This API provides comprehensive vocabulary management with AI-powered features including example generation and text-to-speech capabilities.

## Goal
Vocabloom is our capstone project designed for **English learners**, especially those studying English as a second language (ESL).  
It helps users build and organize their vocabulary with tools that go beyond a basic dictionary.

**Our mission is to transform vocabulary learning from passive memorization into an active, personalized experience.**

## Highlights
- **Smart Word Search** — Get phonetics, audio, part of speech, meanings, definitions, and examples using a third party dictionary API
- **Personal Vocabulary Collection** — Save and tag words for easy review
- **Custom Word** — Add your own words with personalized meanings, phonetics, and tags  
- **Personal Notes & Examples** — Keep your own notes and example sentences for each word  
- **Amazon Polly Audio** — Listen the examples in natural-sounding speech  
- **AI Examples** — Generate examples with Gemini AI by difficulty and context  
- **Mobile-First Design** — Works great on phone, tablet, or desktop 

## Related Links

- **Frontend Repository**: [VocaBloom Frontend](https://github.com/aigerimdev/vocabloom-frontend)
- **Live Application**: [VocaBloom App](https://vocabloomapp.netlify.app/)
- **API Documentation**: [Swagger UI](https://vocabloom-backend.onrender.com/api/schema/swagger-ui/) 

## Features

### Core Functionality
- **User Authentication**: JWT-based authentication with registration, login, and token refresh
- **Tag Management**: Organize vocabulary words with custom tags/categories
- **Word Management**: Full CRUD operations for vocabulary words with meanings and definitions
- **User Examples**: Create and manage custom example sentences for words
- **Audio Generation**: Text-to-speech conversion using Amazon Polly 
- **AI Integration**: Generate example sentences using Google Gemini AI

### API Highlights
- RESTful API design with comprehensive endpoints
- User data isolation and security
- Nested serialization for word structures
- Interactive API documentation with Swagger/ReDoc
- Test coverage

## Technology Stack

- **Framework**: Django + Django REST Framework
- **Database**: Amazon RDS PostgreSQL (production) / PostgreSQL (local) / SQLite (testing)
- **Authentication**: JWT with SimpleJWT
- **AI Services**: Google Gemini API for example generation
- **Audio Services**: Amazon Polly for text-to-speech
- **Documentation**: drf-spectacular (OpenAPI/Swagger/reDoc)
- **Testing**: Django TestCase
- **Deployment**: Render (production)
- **Cloud Services**: AWS (RDS, Polly)

## Frontend Integration

This backend powers the [VocaBloom React Native frontend](https://github.com/aigerimdev/vocabloom-frontend). 

**Try the Live App**: [vocabloomapp.netlify.app](https://vocabloomapp.netlify.app/)


## Prerequisites

- Python 3.9+
- PostgreSQL (for local development)
- Google Gemini API key
- AWS credentials for Polly service and RDS database access
- Amazon RDS PostgreSQL instance (for production)

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd vocabloom_backend
python -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your actual values
```

Required environment variables:
```env
# Development
SECRET_KEY=your-secret-key-here
DEBUG=True
LOCAL_DATABASE_URL=postgres://username:password@localhost:5432/vocabloom_development

# Production
DATABASE_URL=postgres://db_username:db_password@your-rds-endpoint.amazonaws.com:5432/postgres

# AWS Services
GEMINI_API_KEY=your-gemini-api-key
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
```

### 3. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run Development Server
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

**Test with Frontend**: Clone the [frontend repo](https://github.com/aigerimdev/vocabloom-frontend) and connect it to your local backend!

## Database Configuration

### Local Development
```bash
# Install and setup PostgreSQL locally
brew install postgresql

# Create local database
createdb vocabloom_development

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### Production (Amazon RDS)
The production environment uses Amazon RDS PostgreSQL.

**RDS Connection String Format:**
```
postgres://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/database_name
```
## Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test Categories
```bash
python manage.py test vocabloom.tests.test_authentication
python manage.py test vocabloom.tests.test_words
python manage.py test vocabloom.tests.test_gemini_service

## API Documentation

### Interactive Documentation
- **Swagger UI**: `https://vocabloom-backend.onrender.com/api/schema/swagger-ui/`
- **ReDoc**: `https://vocabloom-backend.onrender.com/api/schema/redoc/`
- **OpenAPI Schema**: `https://vocabloom-backend.onrender.com/api/schema/`

### Core Endpoints

#### Authentication
```
POST /api/register_user/     # User registration
POST /api/token/             # Login (get tokens)
POST /api/token/refresh/     # Refresh access token
POST /api/logout/            # Logout
GET  /api/authenticated/     # Check auth status
```

#### Tags
```
GET    /api/tags/           # List user's tags
POST   /api/tags/           # Create new tag
GET    /api/tags/{id}/      # Get specific tag
PUT    /api/tags/{id}/      # Update tag
DELETE /api/tags/{id}/      # Delete tag
```

#### Words
```
GET    /api/words/                    # List user's words
POST   /api/words/                    # Create new word
GET    /api/words/{id}/               # Get specific word
PATCH  /api/words/{id}/               # Update word (note only)
DELETE /api/words/{id}/               # Delete word
GET    /api/tags/{id}/words/          # Get words by tag
```

#### User Examples
```
GET    /api/words/{word_id}/examples/                    # List examples for word
POST   /api/words/{word_id}/examples/create/             # Create example
GET    /api/words/{word_id}/examples/{example_id}/       # Get specific example
PUT    /api/words/{word_id}/examples/{example_id}/       # Update example
DELETE /api/words/{word_id}/examples/{example_id}/       # Delete example
POST   /api/words/{word_id}/examples/generate/           # Generate AI example
```

#### Audio
```
POST /api/audio/            # Convert text to speech
```

## Project Structure

```
vocabloom_backend/
├── vocabloom_backend/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── vocabloom/                  # Main Django app
│   ├── views/                  # Organized view modules
│   │   ├── auth_views.py
│   │   ├── tag_views.py
│   │   ├── word_views.py
│   │   ├── user_example_views.py
│   │   └── audio_views.py
│   ├── services/               # External service integrations
│   │   ├── gemini_service.py
│   │   └── polly_service.py
│   ├── tests/                  # Test suite
│   │   ├── test_authentication.py
│   │   ├── test_tags.py
│   │   ├── test_words.py
│   │   ├── test_user_examples.py
│   │   ├── test_gemini_service.py
│   │   └── test_polly_service.py
│   ├── models.py               # Database models
│   ├── serializers.py          # API serializers
│   ├── urls.py                 # URL routing
│   └── admin.py                # Django admin configuration
├── requirements.txt
├── .env.example
└── README.md
```

## Full Stack Architecture

```
┌─────────────────┐    HTTP/JSON    ┌──────────────────┐
│  React Native   │ ◄─────────────► │   Django REST    │
│    Frontend     │     API Calls   │     Backend      │
│   (Netlify)     │                 │    (Render)      │
└─────────────────┘                 └──────────────────┘
                                             │
                                             ▼
                                    ┌──────────────────┐
                                    │   Amazon RDS     │
                                    │   PostgreSQL     │
                                    │                  │
                                    │ ┌──────────────┐ │
                                    │ │ Amazon Polly │ │
                                    │ │ (Text-to-    │ │
                                    │ │  Speech)     │ │
                                    │ └──────────────┘ │
                                    └──────────────────┘
```

### AWS Services Used:
- **Amazon RDS**: Managed PostgreSQL database for production data
- **Amazon Polly**: Text-to-speech conversion for audio features
- **AWS IAM**: Secure access management for services
  
## Deployment

### Production Environment Variables
```env
DJANGO_ENV=production
DEBUG=False
DATABASE_URL=postgres://username:password@your-rds-endpoint.amazonaws.com:5432/database
ALLOWED_HOSTS=vocabloom-backend.onrender.com
CORS_ALLOWED_ORIGINS=https://vocabloomapp.netlify.app
```

### Database Setup (Production)
Migrations are automatically run during deployment, but you can manually run them:
```bash
python manage.py migrate
```

**Note**: Ensure your Amazon RDS security groups allow connections from your Render deployment.

## Contributing

1. Fork both repositories:
   - [Backend](https://github.com/your-username/vocabloom-backend)
   - [Frontend](https://github.com/aigerimdev/vocabloom-frontend)
2. Create feature branches (`git checkout -b feature/amazing-feature`)
3. Test your changes with both frontend and backend
4. Submit pull requests to respective repositories

## Acknowledgments

### Ada Developers Academy - Cohort 23
This project is proudly developed as part of **Ada Developers Academy Cohort 23** capstone project. VocaBloom represents the culmination of our intensive full-stack software development journey.

### Team
- **Aigerim Kalygulova** - [GitHub](https://github.com/aigerimdev/)
- **Lina Martinez** - [GitHub](https://github.com/linakl19/)

### Special Thanks
We extend our heartfelt gratitude to:

- **Ada Instructors** - For their expertise, patience, and guidance throughout our learning journey
- **Ada Volunteers** - For sharing their industry knowledge and providing invaluable mentorship
- **Ada Staff** - For creating an inclusive and supportive learning environment
- **Cohort 23 Classmates** - For the collaboration, support, and friendship that made this journey memorable

### Technology Partners
- Django REST Framework for the robust API framework
- SimpleJWT for JWT authentication
- Amazon Web Services (RDS, Polly) for cloud infrastructure
- Google Gemini API for AI-powered features
- PostgreSQL for reliable data storage
- The open-source community for excellent documentation and support

### Ada Mission
This project reflects Ada's mission to diversify the tech industry by preparing women+ and gender-diverse individuals for careers in software development. We're grateful to be part of this transformative program.

---

**Built with ❤️ by Aigerim & Lina | Ada Developers Academy c23 for language learners everywhere!** 🌍📚✨

**🌱 Experience VocaBloom**: [Try the live app](https://vocabloomapp.netlify.app/) | [View frontend code](https://github.com/aigerimdev/vocabloom-frontend)

---