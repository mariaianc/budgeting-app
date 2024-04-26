import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to test OpenAI API key
def test_openai_api_key():
    # Get API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        print("Error: OpenAI API key not found in environment variables.")
        return

    # Create OpenAI client instance with API key
    client = OpenAI(api_key=api_key)

    # Test API key by calling a simple API method
    try:
        # Call OpenAI API with a simple message and specify the model
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a friend."},
                {"role": "user", "content": "Hello, World!"}
            ]
        )
        
        # Accessing the completion text from the response
        completion_text = response.choices[0].message.content
        
        # Print the completion text
        print("API key is working! Completion: ", completion_text)
    except Exception as e:
        print("Error:", e, ". API key is not working.")

# Call the function to test the API key
test_openai_api_key()
