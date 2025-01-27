import os, json, sys
from pymongo import MongoClient
from google.cloud import storage
from datetime import timedelta

def connectToMongo():
    try:
        print(os.getenv('MONGO_URI', 'none'))
        client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/pickler-db'))
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        return client['pickler-db']
    except Exception as e:
        print('Error connecting to MongoDB - ', e)
        return None

def verify_jwt(token=None):
    try:
        JWT_SECRET = os.getenv('JWT_SECRET', '')
        if(JWT_SECRET == ''):
            print('JWT_SECRET not set in environment')
            return False
        if token is None:
            return False
        result = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return result
    except Exception as e:
        print('Error checking API key - ', e)
        return False
    
def connectToGCS():
    try:
        client = storage.Client.from_service_account_json(os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'creds.json'))
        bucket_name = os.getenv('GCS_BUCKET', 'pickler-bucket-test')
        bucket = client.bucket(bucket_name)
        print("Successfully connected to GCS!")
        return bucket
    except Exception as e:
        print('Error connecting to GCS - ', e)
        return None

# def connectToRedis():
#     try:
#         client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=os.getenv('REDIS_PORT', 6379), decode_responses=True)
#         client.ping()
#         print("Successfully connected to Redis!")
#         return client
#     except Exception as e:
#         print('Error connecting to Redis - ', e)
#         return None

def get_signed_url(bucket, object_name, expiration_minutes=60):
    try:
        blob = bucket.blob(object_name)
        signed_url = blob.generate_signed_url(expiration=timedelta(minutes=expiration_minutes))
        return signed_url
    except Exception as e:
        print('Error generating signed URL - ', e)
        return None
    

def save_df_to_gcs(bucket, dataframe, object_name):
    try:
        # Convert dataframe to CSV
        csv_data = dataframe.to_csv(index=False)
        
        # Create a new blob and upload the CSV data
        blob = bucket.blob(object_name)
        blob.upload_from_string(csv_data, content_type='text/csv')
        
        print(f"Successfully uploaded cleaned data to GCS as {object_name}")
        return True
    except Exception as e:
        print('Error saving to GCS - ', e)
        return False
