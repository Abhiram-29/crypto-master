import pandas as pd
import motor.motor_asyncio
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os

load_dotenv()

# Connect to MongoDB
async def connect_to_mongodb(connection_string: str, db_name: str):
    """Connect to MongoDB and return the database object."""
    client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
    return client[db_name]

async def insert_questions(db, collection_name: str, questions: List[Dict[Any, Any]]):
    """Insert questions into specified MongoDB collection."""
    collection = db[collection_name]
    result = await collection.insert_many(questions)
    return result.inserted_ids

def preprocess_excel_data(csv_path: str) -> List[Dict[Any, Any]]:
    """Read Excel file and preprocess data for MongoDB."""
    df = pd.read_csv(csv_path)
    
    # Convert DataFrame to list of dictionaries
    questions = []
    for _, row in df.iterrows():
        # Create options array
        options = []
        for i in range(1, 5):
            option_key = f'option {i}'
            if option_key in row and not pd.isna(row[option_key]):
                options.append(row[option_key])
        
        # Use empty list as default if no options are found
        if not options:
            options = None
        
        if row["Difficulty (Easy/Medium/Hard)"].lower() != "medium":
            continue
        
        # Map dataframe columns to MongoDB document structure
        question = {
            "question_id": row["question_id"],
            "topic": row["Topic"] if "Topic" in row and not pd.isna(row["Topic"]) else "misc",
            "difficulty": row["Difficulty (Easy/Medium/Hard)"].lower() if "Difficulty (Easy/Medium/Hard)" in row and not pd.isna(row["Difficulty (Easy/Medium/Hard)"]) else "medium",
            "hint": row["hint"] if "hint" in row and not pd.isna(row["hint"]) else row["Hint"] if "Hint" in row and not pd.isna(row["Hint"]) else "no hint",
            "question_type": row["question_type (fib/mcq/mcq_image)"] if "question_type (fib/mcq/mcq_image)" in row and not pd.isna(row["question_type (fib/mcq/mcq_image)"]) else "mcq",
            "question": row["question"],
            "options": options,
            "correct_ans": row["answer"],
            "multiplier": row["multiplier"] if "multiplier" in row and not pd.isna(row["multiplier"]) else 1.0,
            "minimum_spend": 125
        }
        
        # Add question_image_url only if it exists and is not NaN
        if "Question Image URL (for mcq_image)" in row and not pd.isna(row["Question Image URL (for mcq_image)"]):
            question["question_image_url"] = row["Question Image URL (for mcq_image)"]
        
        questions.append(question)
    
    return questions

async def main():
    # Configuration
    CONNECTION_STRING = os.getenv("CONNECTION_STRING")   # Update with your MongoDB connection string
    DATABASE_NAME = "CryptoMaster"  # Update with your database name
    CSV_PATH = "Cryptomastes Questions - Sheet1(2).csv"  # Update with your excel file path
    COLLECTION_NAME = "Medium"
    
    # Process Excel data
    questions = preprocess_excel_data(CSV_PATH)
    
    # Connect to MongoDB
    db = await connect_to_mongodb(CONNECTION_STRING, DATABASE_NAME)
    
    # Insert questions
    inserted_ids = await insert_questions(db, COLLECTION_NAME, questions)
    print(f"Inserted {len(inserted_ids)} questions into MongoDB")

if __name__ == "__main__":
    asyncio.run(main())