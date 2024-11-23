from flask import Flask, request, jsonify
import ollama

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.json
    messages = data.get('messages', [])
    
    # Convert messages to Ollama format
    ollama_messages = [{'role': msg['role'], 'content': msg['content']} for msg in messages]
    
    # Generate response using Ollama
    response = ollama.chat(model='llama3.2:1b', messages=ollama_messages)
    
    # Format response to match OpenAI API
    return jsonify({
        'id': 'chatcmpl-' + response['id'],
        'object': 'chat.completion',
        'created': int(response['created']),
        'model': 'llama3.2:3b',
        'choices': [{
            'index': 0,
            'message': {
                'role': 'assistant',
                'content': response['message']['content'],
            },
            'finish_reason': 'stop'
        }],
        'usage': {
            'prompt_tokens': -1,
            'completion_tokens': -1,
            'total_tokens': -1
        }
    })

if __name__ == '__main__':
    app.run(port=8111)