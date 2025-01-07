import requests
import pymongo
import time
import threading
from datetime import datetime
from multiprocessing import Pool
from bson.errors import InvalidBSON

API_KEY = "add-your-api-key"  # Add your API key here
API_URL = "https://api.moderatehatespeech.com/api/v1/moderate/"  # API URL for hate speech moderation

def analyze_toxicity(content):
    CONF_THRESHOLD = 0.9  # Confidence threshold for flagging toxicity
    data = {
        "token": API_KEY,
        "text": content
    }
    try:
        response = requests.post(API_URL, json=data).json()  # API request to analyze toxicity
        if response["class"] == "flag" and float(response["confidence"]) > CONF_THRESHOLD:
            return {"class": response["class"], "confidence": float(response["confidence"])}
        return {"class": response["class"], "confidence": float(response["confidence"])}
    except Exception as e:
        print(f"Error with ModerateHatespeech API: {e}")
        return None

def safe_datetime(utc_timestamp):
    try:
        return datetime.utcfromtimestamp(utc_timestamp).strftime('%Y-%m-%d')  # Convert timestamp to safe datetime format
    except (Exception, InvalidBSON) as e:
        print(f"Invalid date value: {e} for timestamp {utc_timestamp}")
        return "Invalid Date"

def process_batch(db_name, collection_name, text_field, batch_size=100):
    # Initialize MongoDB client inside the worker function
    client = pymongo.MongoClient("mongodb://localhost:27017/", datetime_conversion='DATETIME_AUTO')
    db = client[db_name]
    collection = db[collection_name]

    cursor = collection.find({"toxicity": {"$exists": False}}).limit(batch_size)  # Find documents that haven't been analyzed
    updates = []
    for document in cursor:
        try:
            content = document.get(text_field, "").strip()
            if not content:
                print(f"Skipping document ID: {document['_id']} due to empty content.")  # Skip documents with empty content
                continue

            # Use safe_datetime to handle invalid dates
            post_date = safe_datetime(document.get('created_utc', 0))
            toxicity = analyze_toxicity(content)  # Analyze toxicity of the content
            if toxicity is not None:
                updates.append({"_id": document["_id"], "toxicity": toxicity})  # Add toxicity information to the update
                print(f"Updated document {document['_id']} with toxicity {toxicity}")
        except Exception as e:
            print(f"Error processing document {document['_id']}: {e}")

    # Perform bulk update to minimize number of write operations
    if updates:
        collection.bulk_write([pymongo.UpdateOne({"_id": update["_id"]}, {"$set": update}) for update in updates])  # Update documents in bulk
        print(f"Batch update complete: {len(updates)} documents processed.")

def process_fourchan_threads(db_name, collection_name, batch_size=100):
    # Initialize MongoDB client inside the worker function
    client = pymongo.MongoClient("mongodb://localhost:27017/", datetime_conversion='DATETIME_AUTO')
    db = client[db_name]
    collection = db[collection_name]

    cursor = collection.find({"toxicity_processed": {"$exists": False}}).sort("posts", -1).limit(batch_size)  # Find threads that haven't been processed
    updates = []
    for document in cursor:
        thread_id = document["_id"]
        posts = document.get("posts", [])
        updated_posts = []
        toxicity_scores = []

        for post in posts:
            content = post.get("com", "").strip()
            if not content:
                print(f"Skipping post {post.get('no')} in thread {thread_id} due to empty content.")  # Skip posts with empty content
                updated_posts.append(post)
                continue

            toxicity = analyze_toxicity(content)  # Analyze toxicity of each post
            if toxicity is not None:
                post["toxicity"] = toxicity  # Add toxicity information to the post
                toxicity_scores.append(toxicity["confidence"])

            updated_posts.append(post)

        # Add a summary toxicity score to the thread level
        if toxicity_scores:
            avg_toxicity = sum(toxicity_scores) / len(toxicity_scores)  # Calculate average toxicity score
            thread_toxicity_summary = {
                "average_toxicity": avg_toxicity,
                "highest_toxicity": max(toxicity_scores),
                "lowest_toxicity": min(toxicity_scores),
                "processed_posts": len(toxicity_scores),
                "total_posts": len(posts),
            }
        else:
            thread_toxicity_summary = None

        # Prepare bulk update for thread
        updates.append({
            "_id": thread_id,
            "$set": {
                "posts": updated_posts,
                "toxicity_processed": True,
                "toxicity_summary": thread_toxicity_summary,
            }
        })

    if updates:
        collection.bulk_write([pymongo.UpdateOne(update["_id"], update["$set"]) for update in updates])  # Bulk update threads
        print(f"Batch update complete for {len(updates)} threads.")

def run_parallel_processing():
    db_name = "redditDB"
    pool = Pool(processes=5)  # Create a pool of workers to process batches in parallel
    # reddit
    pool.starmap(process_batch, [(db_name, "comments", "text", 100)], [(db_name, "posts", "text", 100)])
    # fourchan
    process_fourchan_threads("fourchanDB", "threads", batch_size=100)

def main():
    while True:
        run_parallel_processing()  # Continuously run the processing
        time.sleep(5)  # Sleep for 5 seconds before running the process again

if __name__ == "__main__":
    main()  # Start the main function
