import json
import requests

def agent_json(name: str, msg: dict, think=False):
    return {
        'model': name,
        'messages': msg,
        'think': think,
        'stream': False,
        'format': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'x': {'type': 'number'},
                    'y': {'type': 'number'},
                    'vx': {'type': 'number'},
                    'vy': {'type': 'number'}
                },
                'required': ['x', 'y', 'vx', 'vy']
            }
        }
    }

# main
model = 'qwen3:4b'
prompt = 'Generate 2 balls with random velocity: in center of 640x480 and in random place'
messages = []

tick = 0

while True:
    messages.append({'role': 'user', 'content': prompt})
    payload = agent_json(model, messages)
    req = requests.post(url='http://localhost:11434/api/chat', json=payload, stream=True)

    prompt = 'Simulate next physics iteration with provided objects'
    tick += 1

    # simulation
    for msg in req.iter_lines():
        data = json.loads(msg)
        balls = json.loads(data['message']['content'])
        messages.append({'role': 'assistant', 'content': json.dumps(balls)})

        print(f'tick {tick}: {balls}')
