import firebase_admin
import functions_framework
from firebase_admin import firestore
import os

# Get the project ID from the environment variables
PROJECT_ID = os.environ.get('PROJECT_ID')
# Initialize the Firebase app
APP = firebase_admin.initialize_app()

@functions_framework.http
def conversation_start(request):
    """
    This function starts a conversation.
    Parameters:
        request: The HTTP request.
    """  
    if request.method == 'OPTIONS':
        logging.info("Received options request")
        # Preflight request. Reply successfully:
        response = make_response()
        response.headers.set('Access-Control-Allow-Origin', '*')  # Adjust this to allow specific origins
        response.headers.set('Access-Control-Allow-Methods', 'POST')
        response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.set('Access-Control-Max-Age', '3600')
        return response
    # Get the conversation ID from the request body
    conversation_id = request.json.get('conversation_id')
    # Get the model codename from the request body
    model_codename = "gpt-3.5-turbo"
    # Get the user ID from the request body if exists
    user = request.json.get('user')

    # Create a new conversation document
    conversation_ref = firestore.client().collection(u'conversations').document(conversation_id)
    conversation_ref.set({
        u'model_codename': model_codename,
        u'user': user,
        u'messages': []
    })

    # Return a success response
    return 'Conversation started successfully'
