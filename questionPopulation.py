from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Literal
from dotenv import load_dotenv
import json
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from models import MCQ, MCQWithImage, FillInTheBlanks
from pydantic import ValidationError
load_dotenv()

sample_mcqs = [{"_id": 2,"topic": "Python",
        "difficulty": "hard",
        "hint": "Think about data types",
        "question": "What is the output of type(1/2) in Python 3?",
        "options": ["int", "float", "double", "decimal"],
        "correct_ans": "float"
    }]

sample_blanks = [{
    "_id": 3,"topic" : "Java",
    "difficulty" : "hard",
    "hint" : "Bunk",
    "question":"Did you watch pushpa 2",
    "correct_ans" : "yes"
}]

sample_image_mcq = [{
    "_id": 4,"topic" : "HTML",
    "difficulty" : "hard",
    "hint" : "it's not a programming language",
    "question":"https://www.indiabix.com/_files/images/verbal-reasoning/dice/4-13-1-4.png",
    "options" : ["@","$","()","#"],
    "correct_ans" : 1
}]

async def validate_mcq(json_objects: List[dict]) -> List[MCQ]:
    """Validate JSON objects against the Pydantic model."""
    validated_objects = []
    for idx, obj in enumerate(json_objects):
        try:
            validated_obj = FillInTheBlanks(**obj)
            validated_objects.append(validated_obj)
        except ValidationError as e:
            print(f"Validation error in object {idx + 1}:")
            print(e.json())
            continue
    return validated_objects

async def upload_to_mongodb(validated_objects: List[MCQ],
                          mongodb_uri: str,
                          database_name: str,
                          collection_name: str):
    try:
        # Create MongoDB client
        client = AsyncIOMotorClient(mongodb_uri)
        db = client[database_name]
        collection = db[collection_name]

        # Convert Pydantic models to dictionaries and insert
        documents = [obj.dict() for obj in validated_objects]
        if documents:
            result = await collection.insert_many(documents)
            print(f"Successfully inserted {len(result.inserted_ids)} documents")
        else:
            print("No valid documents to insert")

    except Exception as e:
        print(f"Error uploading to MongoDB: {str(e)}")
    finally:
        client.close()

async def main():
    MONGODB_URI = os.getenv("CONNECTION_STRING")
    DATABASE_NAME = "CryptoMaster"
    COLLECTION_NAME = "Hard"

    try:
        validated_objects = await validate_mcq(sample_blanks)
        print(f"Successfully validated {len(validated_objects)} objects")

        await upload_to_mongodb(validated_objects,
                              MONGODB_URI,
                              DATABASE_NAME,
                              COLLECTION_NAME)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    for i in range(15):
        asyncio.run(main())
