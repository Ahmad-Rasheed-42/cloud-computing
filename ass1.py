import requests
import boto3
import json
import uuid
from io import BytesIO

# Configuration
TICKETMASTER_API_KEY = 'AZ5QWB3FqVTTEBo1pMAuMeJFHI1pm4kw'
CITY = 'Paris'
S3_BUCKET_NAME = 'amy-369'
S3_REGION = 'eu-north-1'

# Initialize boto3 S3 client (Relies on the IAM Role attached to the EC2 instance)
s3_client = boto3.client('s3', region_name=S3_REGION)

def fetch_events():
    """Fetches structured JSON data from the Ticketmaster API."""
    url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={TICKETMASTER_API_KEY}&city={CITY}&size=10"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json().get('_embedded', {}).get('events', [])
    return []

def upload_image_to_s3(image_url, event_id):
    """Downloads an event poster and uploads it securely to S3."""
    response = requests.get(image_url)
    if response.status_code == 200:
        # Generate a unique filename
        file_name = f"event_posters/{event_id}_{uuid.uuid4().hex[:6]}.jpg"
        
        # Upload to S3 directly from memory
        s3_client.upload_fileobj(
            BytesIO(response.content),
            S3_BUCKET_NAME,
            file_name,
            ExtraArgs={'ContentType': 'image/jpeg'}
        )
        # Return the S3 object URL
        return f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{file_name}"
    return None

def process_and_store_events():
    """Main workflow to process events and store data."""
    raw_events = fetch_events()
    processed_events = []

    for event in raw_events:
        event_id = event.get('id')
        title = event.get('name')
        date = event.get('dates', {}).get('start', {}).get('localDate')
        
        # Get the highest resolution image available
        images = event.get('images', [])
        image_url = images[0]['url'] if images else None
        
        s3_image_link = None
        if image_url:
            s3_image_link = upload_image_to_s3(image_url, event_id)

        # Structure the data to display as "University Events"
        processed_events.append({
            'event_id': event_id,
            'title': title,
            'date': date,
            'poster_url': s3_image_link,
            'type': 'University Event'
        })

    # Store the processed JSON persistently in S3
    s3_client.put_object(
        Bucket=S3_BUCKET_NAME,
        Key='processed_data/university_events.json',
        Body=json.dumps(processed_events),
        ContentType='application/json'
    )
    print(f"Successfully processed and stored {len(processed_events)} events.")

if __name__ == "__main__":
    process_and_store_events()