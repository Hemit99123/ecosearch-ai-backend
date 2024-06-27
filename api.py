from flask import Flask, jsonify, request
from flask_restful import Api
from openai import OpenAI
import os
from time import sleep
import functions 

app = Flask(__name__)
api = Api(app)


# Setting the api key as an environmental variable

os.environ["OPENAI_API_KEY"] = "the key goes here"

# Home route
@app.route('/')
def home():
    return jsonify({
        'name': 'ecosearch-ai-chatbot',
        'description': 'An assistant that provides answers to EcoSearch search engine related prompts, using OpenAI\'s API model',
        'authors': ['Sungwoo Cho', 'Hemit Patel'],
        'version': '1.0.0',
        'license': 'MIT',
    })

# Chat route
@app.route('/chat', methods=['POST'])
def chat():
    # Initialize OpenAI client
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Retrieve JSON data from request
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('message', '')

    # Check for required parameters
    if not thread_id:
        return jsonify({"error": "Missing thread_id"}), 400

    print(f"Received message: {user_input} for thread ID: {thread_id}")

    # Add user's message to the thread
    client.beta.threads.messages.create(thread_id=thread_id,
                                        role="user",
                                        content=user_input)

    # Create an assistant session
    assistant_id = functions.create_assistant(client)

    # Run the assistant and wait for completion
    while True:
        run = client.beta.threads.runs.create(thread_id=thread_id,
                                              assistant_id=assistant_id)
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                       run_id=run.id)
        print(f"Run status: {run_status.status}")
        if run_status.status == 'completed':
            break
        sleep(1)

    # Retrieve and return the latest message from the assistant
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value

    print(f"Assistant response: {response}")
    return jsonify({"response": response})

# Run the Flask server
if __name__ == '__main__':
    app.run(debug=True)