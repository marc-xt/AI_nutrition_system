"""
Nutrition Recommendation System Backend (Corrected Version)
This script contains the corrected backend implementation with proper database configuration alignment.

Key Fixes:
1. Database Configuration: Proper use of database_config module
2. Base Model: Single source of truth for SQLAlchemy Base
3. Session Management: Consistent database session handling
4. Import Structure: Clean import hierarchy

Setup Instructions:
1. Install dependencies: pip install -r requirements.txt
2. Copy .env.example to .env and configure your settings
3. Run this script to initialize the system
"""

# Install required packages if not already installed
# !pip install -r requirements.txt

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database imports - use database_config module (CORRECTED)
from database_config import engine, SessionLocal, Base, init_db, test_connection, get_database_url
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON

# Machine Learning imports
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Web framework imports
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uvicorn

print("✅ All dependencies imported successfully!")
print(f"📊 Database URL: {get_database_url()}")

# Database Models (CORRECTED - using Base from database_config)
# Note: Base is imported from database_config to avoid conflicts

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    age = Column(Integer)
    gender = Column(String)
    weight = Column(Float)  # kg
    height = Column(Float)  # cm
    activity_level = Column(String)  # sedentary, light, moderate, active, very_active
    dietary_preferences = Column(JSON)  # vegetarian, vegan, gluten-free, etc.
    allergies = Column(JSON)  # list of allergies
    health_goals = Column(JSON)  # weight_loss, muscle_gain, maintenance, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meal_logs = relationship("MealLog", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")

class Food(Base):
    __tablename__ = "foods"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String)
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float)
    carbs_per_100g = Column(Float)
    fat_per_100g = Column(Float)
    fiber_per_100g = Column(Float)
    sugar_per_100g = Column(Float)
    sodium_per_100g = Column(Float)
    vitamins = Column(JSON)  # dict of vitamin names and amounts
    minerals = Column(JSON)  # dict of mineral names and amounts
    category = Column(String)  # fruits, vegetables, proteins, grains, dairy, etc.
    barcode = Column(String)
    api_source = Column(String)  # nutritionix, usda, manual
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    meal_items = relationship("MealItem", back_populates="food")

class MealLog(Base):
    __tablename__ = "meal_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    meal_type = Column(String)  # breakfast, lunch, dinner, snack
    date = Column(DateTime)
    total_calories = Column(Float)
    total_protein = Column(Float)
    total_carbs = Column(Float)
    total_fat = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="meal_logs")
    meal_items = relationship("MealItem", back_populates="meal_log")

class MealItem(Base):
    __tablename__ = "meal_items"
    
    id = Column(Integer, primary_key=True, index=True)
    meal_log_id = Column(Integer, ForeignKey("meal_logs.id"))
    food_id = Column(Integer, ForeignKey("foods.id"))
    quantity_grams = Column(Float)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    
    # Relationships
    meal_log = relationship("MealLog", back_populates="meal_items")
    food = relationship("Food", back_populates="meal_items")

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("foods.id"))
    score = Column(Float)  # recommendation score 0-1
    reason = Column(Text)  # why this food is recommended
    meal_type = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    is_accepted = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")

print("✅ Database models defined using centralized Base!")

# Database Configuration and Initialization (CORRECTED)

def setup_database():
    """Setup database and create tables with proper error handling"""
    try:
        print(f"🔗 Connecting to database: {get_database_url()}")
        
        # Test connection first
        if test_connection():
            # Create all tables using the imported Base
            Base.metadata.create_all(bind=engine)
            print("✅ Database setup completed successfully!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

# Setup database
db_success = setup_database()

# Verify database session management
def test_session_management():
    """Test database session management"""
    try:
        db = SessionLocal()
        # Test a simple query
        from sqlalchemy import text
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [row[0] for row in result.fetchall()]
        print(f"📋 Database tables created: {tables}")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Session management error: {e}")
        return False

if db_success:
    test_session_management()

# Nutrition Calculator Class (UNCHANGED - already correct)
class NutritionCalculator:
    """Calculate nutritional requirements and recommendations"""
    
    def __init__(self):
        self.activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
    
    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor equation"""
        if gender.lower() == 'male':
            return 10 * weight + 6.25 * height - 5 * age + 5
        else:
            return 10 * weight + 6.25 * height - 5 * age - 161
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Calculate Total Daily Energy Expenditure"""
        multiplier = self.activity_multipliers.get(activity_level.lower(), 1.55)
        return bmr * multiplier
    
    def calculate_macros(self, tdee: float, goal: str) -> Dict[str, float]:
        """Calculate macronutrient distribution based on goals"""
        if goal == 'weight_loss':
            # 40% protein, 30% carbs, 30% fat
            protein_calories = tdee * 0.4
            carb_calories = tdee * 0.3
            fat_calories = tdee * 0.3
        elif goal == 'muscle_gain':
            # 30% protein, 50% carbs, 20% fat
            protein_calories = tdee * 0.3
            carb_calories = tdee * 0.5
            fat_calories = tdee * 0.2
        else:  # maintenance
            # 25% protein, 45% carbs, 30% fat
            protein_calories = tdee * 0.25
            carb_calories = tdee * 0.45
            fat_calories = tdee * 0.3
        
        return {
            'protein': protein_calories / 4,  # 4 calories per gram
            'carbs': carb_calories / 4,
            'fat': fat_calories / 9  # 9 calories per gram
        }
    
    def calculate_daily_requirements(self, user_data: Dict) -> Dict:
        """Calculate complete daily nutritional requirements"""
        bmr = self.calculate_bmr(
            user_data['weight'], 
            user_data['height'], 
            user_data['age'], 
            user_data['gender']
        )
        
        tdee = self.calculate_tdee(bmr, user_data['activity_level'])
        macros = self.calculate_macros(tdee, user_data.get('goal', 'maintenance'))
        
        return {
            'bmr': bmr,
            'tdee': tdee,
            'calories': tdee,
            'protein': macros['protein'],
            'carbs': macros['carbs'],
            'fat': macros['fat'],
            'fiber': 25 + (user_data['weight'] / 10),  # 25g base + 1g per 10kg
            'water': user_data['weight'] * 0.033  # 33ml per kg
        }

# Test the calculator
calc = NutritionCalculator()
test_user = {
    'weight': 70,
    'height': 175,
    'age': 30,
    'gender': 'male',
    'activity_level': 'moderate',
    'goal': 'maintenance'
}

requirements = calc.calculate_daily_requirements(test_user)
print("✅ Nutrition Calculator initialized!")
print(f"Sample daily requirements: {requirements}")

# Recommendation Engine (CORRECTED - improved session management)
class RecommendationEngine:
    """AI-powered food recommendation system with proper session handling"""
    
    def __init__(self):
        self.nutrition_calc = NutritionCalculator()
        self.scaler = StandardScaler()
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile and preferences with proper session management"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return None
            
            return {
                'id': user.id,
                'age': user.age,
                'gender': user.gender,
                'weight': user.weight,
                'height': user.height,
                'activity_level': user.activity_level,
                'dietary_preferences': user.dietary_preferences or [],
                'allergies': user.allergies or [],
                'health_goals': user.health_goals or ['maintenance']
            }
        finally:
            db.close()
    
    def get_food_database(self) -> pd.DataFrame:
        """Get all foods from database as DataFrame with proper session handling"""
        db = SessionLocal()
        try:
            foods = db.query(Food).all()
            food_data = []
            
            for food in foods:
                food_data.append({
                    'id': food.id,
                    'name': food.name,
                    'category': food.category,
                    'calories': food.calories_per_100g,
                    'protein': food.protein_per_100g,
                    'carbs': food.carbs_per_100g,
                    'fat': food.fat_per_100g,
                    'fiber': food.fiber_per_100g
                })
            
            return pd.DataFrame(food_data)
        finally:
            db.close()
    
    def filter_foods_by_preferences(self, foods_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
        """Filter foods based on user preferences and allergies"""
        filtered_foods = foods_df.copy()
        
        # Filter by dietary preferences
        preferences = user_profile.get('dietary_preferences', [])
        if 'vegetarian' in preferences:
            filtered_foods = filtered_foods[~filtered_foods['category'].isin(['meat', 'fish', 'poultry'])]
        if 'vegan' in preferences:
            filtered_foods = filtered_foods[~filtered_foods['category'].isin(['meat', 'fish', 'poultry', 'dairy', 'eggs'])]
        if 'gluten-free' in preferences:
            filtered_foods = filtered_foods[~filtered_foods['category'].isin(['wheat', 'barley', 'rye'])]
        
        # Filter by allergies (simplified - would need more sophisticated allergen database)
        allergies = user_profile.get('allergies', [])
        for allergy in allergies:
            filtered_foods = filtered_foods[~filtered_foods['name'].str.contains(allergy, case=False, na=False)]
        
        return filtered_foods
    
    def calculate_nutrition_scores(self, foods_df: pd.DataFrame, target_macros: Dict) -> pd.DataFrame:
        """Calculate nutrition scores for foods based on target macros"""
        if foods_df.empty:
            return foods_df
        
        # Normalize nutritional values
        nutrition_features = ['calories', 'protein', 'carbs', 'fat', 'fiber']
        available_features = [f for f in nutrition_features if f in foods_df.columns]
        
        if not available_features:
            foods_df['nutrition_score'] = 0.5
            return foods_df
        
        # Create target vector
        target_vector = np.array([target_macros.get(f.split('_')[0], 0) for f in available_features]).reshape(1, -1)
        
        # Scale the data
        scaler = StandardScaler()
        food_features_scaled = scaler.fit_transform(foods_df[available_features])
        target_scaled = scaler.transform(target_vector)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(food_features_scaled, target_scaled).flatten()
        
        # Add score to dataframe
        foods_df['nutrition_score'] = similarities
        
        return foods_df
    
    def generate_recommendations(self, user_id: int, meal_type: str = 'any', limit: int = 10) -> List[Dict]:
        """Generate personalized food recommendations"""
        user_profile = self.get_user_profile(user_id)
        if not user_profile:
            return []
        
        # Calculate daily requirements
        daily_reqs = self.nutrition_calc.calculate_daily_requirements(user_profile)
        
        # Adjust for meal type
        meal_multipliers = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'dinner': 0.35,
            'snack': 0.15,
            'any': 0.3
        }
        
        multiplier = meal_multipliers.get(meal_type.lower(), 0.3)
        target_macros = {
            'calories': daily_reqs['calories'] * multiplier,
            'protein': daily_reqs['protein'] * multiplier,
            'carbs': daily_reqs['carbs'] * multiplier,
            'fat': daily_reqs['fat'] * multiplier,
            'fiber': daily_reqs['fiber'] * multiplier
        }
        
        # Get and filter foods
        foods_df = self.get_food_database()
        filtered_foods = self.filter_foods_by_preferences(foods_df, user_profile)
        
        # Calculate scores
        scored_foods = self.calculate_nutrition_scores(filtered_foods, target_macros)
        
        # Sort by score and return top recommendations
        top_foods = scored_foods.nlargest(limit, 'nutrition_score')
        
        recommendations = []
        for _, food in top_foods.iterrows():
            recommendations.append({
                'food_id': food['id'],
                'name': food['name'],
                'category': food['category'],
                'score': food['nutrition_score'],
                'reason': f"Matches your nutritional targets for {meal_type}",
                'nutrition_per_100g': {
                    'calories': food.get('calories', 0),
                    'protein': food.get('protein', 0),
                    'carbs': food.get('carbs', 0),
                    'fat': food.get('fat', 0),
                    'fiber': food.get('fiber', 0)
                }
            })
        
        return recommendations

print("✅ Recommendation Engine initialized with proper session management!")

# Sample Data Generation (CORRECTED - proper session handling)
def create_sample_data():
    """Create sample food database and users for testing"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_foods = db.query(Food).count()
        if existing_foods > 0:
            print(f"📊 Database already has {existing_foods} foods. Skipping sample data creation.")
            user_count = db.query(User).count()
            if user_count > 0:
                return db.query(User).first().id
        
        # Sample foods
        sample_foods = [
            Food(name="Chicken Breast", category="meat", calories_per_100g=165, 
                protein_per_100g=31, carbs_per_100g=0, fat_per_100g=3.6, fiber_per_100g=0),
            Food(name="Brown Rice", category="grains", calories_per_100g=111,
                protein_per_100g=2.6, carbs_per_100g=23, fat_per_100g=0.9, fiber_per_100g=1.8),
            Food(name="Broccoli", category="vegetables", calories_per_100g=34,
                protein_per_100g=2.8, carbs_per_100g=7, fat_per_100g=0.4, fiber_per_100g=2.6),
            Food(name="Banana", category="fruits", calories_per_100g=89,
                protein_per_100g=1.1, carbs_per_100g=23, fat_per_100g=0.3, fiber_per_100g=2.6),
            Food(name="Almonds", category="nuts", calories_per_100g=579,
                protein_per_100g=21, carbs_per_100g=22, fat_per_100g=50, fiber_per_100g=12),
            Food(name="Greek Yogurt", category="dairy", calories_per_100g=59,
                protein_per_100g=10, carbs_per_100g=3.6, fat_per_100g=0.4, fiber_per_100g=0),
            Food(name="Salmon", category="fish", calories_per_100g=208,
                protein_per_100g=20, carbs_per_100g=0, fat_per_100g=13, fiber_per_100g=0),
            Food(name="Quinoa", category="grains", calories_per_100g=120,
                protein_per_100g=4.4, carbs_per_100g=21, fat_per_100g=1.9, fiber_per_100g=2.8),
            Food(name="Spinach", category="vegetables", calories_per_100g=23,
                protein_per_100g=2.9, carbs_per_100g=3.6, fat_per_100g=0.4, fiber_per_100g=2.2),
            Food(name="Eggs", category="protein", calories_per_100g=155,
                protein_per_100g=13, carbs_per_100g=1.1, fat_per_100g=11, fiber_per_100g=0)
        ]
        
        # Add foods to database
        for food in sample_foods:
            db.add(food)
        
        # Sample user
        sample_user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_here",
            age=30,
            gender="male",
            weight=70,
            height=175,
            activity_level="moderate",
            dietary_preferences=["vegetarian"],
            allergies=["nuts"],
            health_goals=["maintenance"]
        )
        
        db.add(sample_user)
        db.commit()
        
        print(f"✅ Created {len(sample_foods)} sample foods and 1 sample user")
        return sample_user.id
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        return None
    finally:
        db.close()

# Create sample data
sample_user_id = create_sample_data()

# Test the Recommendation System (CORRECTED)
if sample_user_id and db_success:
    # Initialize recommendation engine
    rec_engine = RecommendationEngine()
    
    # Generate recommendations for different meal types
    meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    
    for meal_type in meal_types:
        print(f"\n🍽️  {meal_type.title()} Recommendations:")
        recommendations = rec_engine.generate_recommendations(sample_user_id, meal_type, limit=3)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec['name']} (Score: {rec['score']:.3f})")
                print(f"   Category: {rec['category']}")
                print(f"   Reason: {rec['reason']}")
                print(f"   Calories: {rec['nutrition_per_100g']['calories']} per 100g")
                print()
        else:
            print("   No recommendations available")
    
    print("✅ Recommendation system test completed!")
else:
    print("❌ Cannot test recommendations - missing user or database connection")

# FastAPI Application Setup (CORRECTED - proper imports)

# Pydantic models for API
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    age: int
    gender: str
    weight: float
    height: float
    activity_level: str
    dietary_preferences: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    health_goals: Optional[List[str]] = []

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: int
    gender: str
    weight: float
    height: float
    activity_level: str
    dietary_preferences: List[str]
    allergies: List[str]
    health_goals: List[str]

class FoodResponse(BaseModel):
    id: int
    name: str
    category: str
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    fiber_per_100g: float

class RecommendationResponse(BaseModel):
    food_id: int
    name: str
    category: str
    score: float
    reason: str
    nutrition_per_100g: dict

# Initialize FastAPI app
app = FastAPI(title="Nutrition Recommendation System", version="1.0.0")

# Security
security = HTTPBearer()

# API Endpoints
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Nutrition Recommendation System API"}

@app.post("/users/", response_model=UserResponse, tags=["Users"])
async def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        # Hash password (simplified - use proper hashing in production)
        hashed_password = user.password + "_hashed"  # Replace with proper hashing
        
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            age=user.age,
            gender=user.gender,
            weight=user.weight,
            height=user.height,
            activity_level=user.activity_level,
            dietary_preferences=user.dietary_preferences,
            allergies=user.allergies,
            health_goals=user.health_goals
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.get("/users/{user_id}", response_model=UserResponse, tags=["Users"])
async def get_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()

@app.get("/foods/", response_model=List[FoodResponse], tags=["Foods"])
async def get_foods():
    db = SessionLocal()
    try:
        foods = db.query(Food).all()
        return foods
    finally:
        db.close()

@app.get("/recommendations/{user_id}", response_model=List[RecommendationResponse], tags=["Recommendations"])
async def get_recommendations(user_id: int, meal_type: str = "any", limit: int = 10):
    try:
        rec_engine = RecommendationEngine()
        recommendations = rec_engine.generate_recommendations(user_id, meal_type, limit)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nutrition/{user_id}", tags=["Nutrition"])
async def get_nutrition_requirements(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        calc = NutritionCalculator()
        user_data = {
            'weight': user.weight,
            'height': user.height,
            'age': user.age,
            'gender': user.gender,
            'activity_level': user.activity_level,
            'goal': user.health_goals[0] if user.health_goals else 'maintenance'
        }
        
        requirements = calc.calculate_daily_requirements(user_data)
        return requirements
    finally:
        db.close()

print("✅ FastAPI application configured with proper database integration!")

# Database Configuration Verification
def verify_system_integrity():
    """Verify all system components are properly configured"""
    print("🔍 System Integrity Check:")
    
    # 1. Database Configuration
    print(f"✅ Database URL: {get_database_url()}")
    
    # 2. Database Connection
    if test_connection():
        print("✅ Database connection: OK")
    else:
        print("❌ Database connection: FAILED")
        return False
    
    # 3. Table Creation
    db = SessionLocal()
    try:
        from sqlalchemy import text
        tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        table_names = [table[0] for table in tables]
        expected_tables = ['users', 'foods', 'meal_logs', 'meal_items', 'recommendations']
        
        for table in expected_tables:
            if table in table_names:
                print(f"✅ Table '{table}': OK")
            else:
                print(f"❌ Table '{table}': MISSING")
    finally:
        db.close()
    
    # 4. Sample Data
    if sample_user_id:
        print(f"✅ Sample user ID: {sample_user_id}")
    else:
        print("❌ Sample data: NOT CREATED")
    
    # 5. Recommendation Engine
    try:
        rec_engine = RecommendationEngine()
        print("✅ Recommendation Engine: OK")
    except Exception as e:
        print(f"❌ Recommendation Engine: ERROR - {e}")
    
    print("\n🎯 System verification completed!")
    return True

# Run verification
verify_system_integrity()

print("\n🚀 System ready! To start the API server, run:")
print("   uvicorn Backend_nutrition_corrected:app --host 0.0.0.0 --port 8000 --reload")
print("\n📚 API Documentation will be available at: http://localhost:8000/docs")
