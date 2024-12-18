import json
import boto3
import base64
import uuid

# Initialize Rekognition client
rekognition = boto3.client('rekognition')

def lambda_handler(event, context):
    if event['httpMethod'] == 'POST':
        body = json.loads(event['body'])
        image_data = body.get('image')

        if not image_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'status': 'error', 'message': 'No image provided'})
            }

        image_bytes = base64.b64decode(image_data)

        response = rekognition.detect_labels(
            Image={'Bytes': image_bytes},
            MaxLabels=10,
            MinConfidence=50
        )

        labels = response['Labels']
        if not labels:
            return {
                'statusCode': 400,
                'body': json.dumps({'status': 'error', 'message': 'No labels detected'})
            }

        animal_labels = [label for label in labels if label['Name'].lower() in ['cat', 'dog', 'elephant', 'horse', 'lion', 'giant panda', 'tiger', 'bird', 'rabbit']]
        if not animal_labels:
            return {
                'statusCode': 400,
                'body': json.dumps({'status': 'error', 'message': 'No animal detected'})
            }

        top_animal = max(animal_labels, key=lambda x: x['Confidence'])

        caption = f"This image contains a {top_animal['Name']}."

        image_id = str(uuid.uuid4())

        
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'success',
                'caption': caption,
                'image_id': image_id,
                'image_url': 'data:image/png;base64,' + image_data  # Return base64 image
            })
        }
    else:
        return {
            'statusCode': 405,
            'body': json.dumps({'status': 'error', 'message': 'Method not allowed'})
        }
