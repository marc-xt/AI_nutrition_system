# Nutrition Recommendation System

A comprehensive backend system for personalized nutrition recommendations using AI and machine learning.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Set database URL, API keys, etc.
```

### 3. Database Setup
The system supports both SQLite (default) and PostgreSQL:

#### SQLite (Default)
```bash
# No additional setup needed - uses local file
```

#### PostgreSQL
```bash
# Install PostgreSQL
# Create database
createdb nutrition_db

# Update .env with PostgreSQL settings
DATABASE_URL=postgresql://user:password@localhost:5432/nutrition_db
```

### 4. Run the System

#### Option A: Jupyter Notebook
```bash
jupyter notebook Backend_nutrition.ipynb
```
Run cells sequentially to set up database and test the system.

#### Option B: FastAPI Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 Dependencies

### Core Dependencies
- **FastAPI** (0.104.1) - Web framework
- **SQLAlchemy** (2.0.23) - Database ORM
- **Pydantic** (2.5.0) - Data validation
- **Uvicorn** (0.24.0) - ASGI server

### Database
- **psycopg2-binary** (2.9.9) - PostgreSQL adapter
- **Alembic** (1.12.1) - Database migrations

### Machine Learning & Data
- **pandas** (2.1.3) - Data manipulation
- **numpy** (1.25.2) - Numerical computing
- **scikit-learn** (1.3.2) - Machine learning
- **scipy** (1.11.4) - Scientific computing

### Authentication & Security
- **python-jose** (3.3.0) - JWT tokens
- **passlib** (1.7.4) - Password hashing
- **python-decouple** (3.8) - Environment variables

### Utilities
- **python-dotenv** (1.0.0) - Environment file loading
- **loguru** (0.7.2) - Logging
- **requests** (2.31.0) - HTTP client

## 🗄️ Database Configuration

### Models
- **User** - User profiles and preferences
- **Food** - Food database with nutritional info
- **MealLog** - Daily meal tracking
- **MealItem** - Individual meal components
- **Recommendation** - AI-generated recommendations

### Database URL Examples
```bash
# SQLite
DATABASE_URL=sqlite:///nutrition_system.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/nutrition_db
```

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///nutrition_system.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (optional)
NUTRITIONIX_API_KEY=your-api-key
USDA_API_KEY=your-api-key

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints
- `POST /users/` - Create user
- `GET /users/{user_id}` - Get user info
- `GET /foods/` - Get food database
- `GET /recommendations/{user_id}` - Get recommendations
- `GET /nutrition/{user_id}` - Get nutrition requirements

## 🤖 Features

### Nutrition Calculator
- BMR calculation (Mifflin-St Jeor equation)
- TDEE calculation with activity levels
- Macronutrient distribution based on goals
- Daily nutritional requirements

### AI Recommendation Engine
- Personalized food recommendations
- Dietary preference filtering
- Allergy consideration
- Meal-type specific suggestions
- Nutritional similarity scoring

### User Profiles
- Personal information (age, gender, weight, height)
- Activity levels
- Dietary preferences (vegetarian, vegan, etc.)
- Allergies and restrictions
- Health goals (weight loss, muscle gain, etc.)

## 🧪 Testing

The notebook includes sample data and tests:
- Sample food database (10 items)
- Test user profile
- Recommendation generation for all meal types
- Nutrition calculation examples

## 🔒 Security Notes

- Password hashing should be implemented properly (currently simplified)
- JWT authentication needs proper implementation
- API keys should be kept secure
- Input validation should be enhanced

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
- Use PostgreSQL in production
- Set proper SECRET_KEY
- Configure CORS for frontend
- Set up proper logging
- Configure reverse proxy (nginx)

## 📈 Future Enhancements

1. **Authentication System** - Complete JWT implementation
2. **External APIs** - Nutritionix, USDA food database
3. **Advanced ML** - Deep learning for recommendations
4. **Mobile API** - Optimized endpoints for mobile
5. **Analytics** - User progress tracking
6. **Meal Planning** - Automated meal plans
7. **Social Features** - Sharing and community

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check DATABASE_URL in .env
# Ensure PostgreSQL is running (if using PostgreSQL)
# Check file permissions (if using SQLite)
```

**Import Errors**
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python version (3.8+ recommended)
python --version
```

**Port Already in Use**
```bash
# Kill process on port 8000
# Or use different port
uvicorn main:app --port 8001
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the notebook examples
3. Check API documentation at /docs
4. Verify environment configuration

## 📄 License

This project is for educational purposes. Please ensure compliance with API terms of service for any external nutrition APIs used.
