from fastapi import FastAPI
from pymongo import MongoClient
import os

app = FastAPI()

# Connect to MongoDB
MONGO_URI = os.environ.get("MONGODB_URI")
client = MongoClient(MONGO_URI)
db = client["adaptive_learning"]

@app.get("/")
def read_root():
    return {"message": "Adaptive Learning Platform API"}

@app.get("/courses")
def get_courses():
    courses = list(db.courses.find({}))
    for course in courses:
        course["_id"] = str(course["_id"])
    return {"courses": courses}