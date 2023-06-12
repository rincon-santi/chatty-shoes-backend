import firebase_admin
import functions_framework
from firebase_admin import firestore
from flask import make_response
import os
import json
import uuid
import openai

# Get the project ID from the environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
# Initialize the Firebase app
APP = firebase_admin.initialize_app()
# Set the OpenAI API key
API_KEY = os.environ.get('OPENAI_KEY')
openai.api_key = API_KEY

@functions_framework.http
def conversation_start(request):
    """
    This function starts a conversation.
    Parameters:
        request: The HTTP request.
    """
    # Pre-flight request. Reply successfully:
    response = make_response()
    response.headers.set('Access-Control-Allow-Origin', '*')  # Adjust this to allow specific origins
    response.headers.set('Access-Control-Allow-Methods', 'POST')
    response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.set('Access-Control-Max-Age', '3600')

    if request.method == 'OPTIONS':
        print("Received options request")
        return response

    # Get the conversation ID from the request body
    conversation_id = str(request.json.get('conversationId'))
    if not conversation_id:  # If the conversation ID is empty
        conversation_id = str(uuid.uuid4())  # Create a new one

    # Get the model codename from the request body
    model_codename = "gpt-3.5-turbo"
    # Get the user ID from the request body if exists
    user = str(request.json.get('user'))
    
    country_code = str(request.json.get('countryCode', 'UK'))
    # Prepare prompt for language model
    messages = [
        {"role": "system", "content": "Act as a language identifier. You will be prompted with a country code and you will answer greeting the user in the corresponding language"},
        {"role":"user", "content": country_code}
    ]

    # Get the greeting from the language model
    full_prompt = {
        "model": model_codename,
        "messages": messages
    }
    response_prompt = openai.ChatCompletion.create(**full_prompt)
    greeting = response_prompt['choices'][0]['message']['content']

    initial_msg = {
        'role': 'assistant',
        'author': 'conversation-builder',
        'content': greeting
    }

    # Create a new conversation document
    conversation_ref = firestore.client().collection(u'conversations').document(conversation_id)
    conversation_ref.set({
        u'model_codename': model_codename,
        u'user': user,
        u'messages': [initial_msg]
    })

    # Set the conversation ID in the response
    response.data = json.dumps({'message': initial_msg['content'], 'conversationId': conversation_id})
    response.headers.set('Content-Type', 'application/json')  # Make sure to set the content type to JSON
    return response
