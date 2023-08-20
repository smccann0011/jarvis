# source ~/Desktop/CypressLabs/.venv/bin/activate
# python3 app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import openai
from dotenv import load_dotenv, find_dotenv

from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

app = Flask(__name__)
CORS(app)

app.logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
app.logger.addHandler(stream_handler)

# read local .env file
print(">> Loading environment variables...")
_ = load_dotenv(find_dotenv()) 

openai.api_key  = os.getenv('OPENAI_API_KEY')
#print(openai.api_key)
#print(os.getenv("SERPAPI_API_KEY"))
#print(os.getenv("WOLFRAM_ALPHA_APPID"))

##============================================================================

@app.route("/api/agent1", methods=["POST"])
def agent1():
    data = request.get_json()
    user_message = data["message"]
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    llm = OpenAI(temperature=0)

    tool_names = ['serpapi']
    #tool_names = ['serpapi', 'wolfram-alpha']
    tools = load_tools(tool_names)

    agent = initialize_agent(tools, llm, agent='zero-shot-react-description', verbose=True)

    app.logger.info('Processing agent request: ' + user_message)
    response = agent.run(user_message)
    app.logger.info('Received response: ' + response)
    return jsonify({'response': response})

##============================================================================

@app.route("/api/chain1", methods=["POST"])
def chain1():
    data = request.get_json()
    user_message = data["message"]
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400
    
    chat_llm = ChatOpenAI(temperature=0)

    # "Translate this sentence from English to French. I love programming."
    messages = [
        SystemMessage(content="You are a helpful assistant that translates English to French."),
        HumanMessage(content=user_message)
    ]
    response = chat_llm(messages)
    app.logger.info('Received response: ' + response.content)
    return jsonify({'response': response.content})

##============================================================================

@app.route("/api/chat2", methods=["POST"])
def chat2():
    data = request.get_json()
    user_message = data["message"]
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        model="gpt-3.5-turbo"
        messages = [{"role": "user", "content": user_message}]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0
        )
        app.logger.info('Received response: ' + response.choices[0].message["content"])
        #return jsonify({'response': response.choices[0].message["content"]})
        return {'response': response.choices[0].message["content"]}

    except Exception as e:
        #app.logger.info(f'Error: {e.message}')
        #print(f"Error: {e}")
        app.logger.info(type(e))
        app.logger.info(e.args)
        app.logger.info(e)
        return jsonify({'error': 'Something went wrong'}), 500

##============================================================================

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data["message"]

    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        engine = 'text-davinci-002'
        app.logger.debug("Using engine: " + engine)
        app.logger.debug('Sending request: ' + user_message)

        response = openai.Completion.create(
            engine=engine,
            prompt=f"User: {user_message}\nAI:",
            max_tokens=50,
            n=1,
            stop=None,
            temperature=0.5,
        )

        app.logger.debug('Received response: ' + response.choices[0].text)
        chatgpt_response = response.choices[0].text.strip()

        return jsonify({'response': chatgpt_response})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Something went wrong'}), 500

##============================================================================

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
