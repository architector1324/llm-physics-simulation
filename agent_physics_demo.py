import json
import pygame
import requests
import threading


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
pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("LLM physics simulation")

model = 'qwen3:4b'
prompt = 'Generate 3 balls with random velocity: in center of 640x480 and remaining in random place'
messages = []

tick = 0
running = True
fps_limit = pygame.time.Clock()

balls = []

# simulation thread
def simulate():
    global prompt
    global running
    global balls
    global messages
    global tick

    while running:
        # main
        messages.append({'role': 'user', 'content': prompt})
        payload = agent_json(model, messages)
        req = requests.post(url='http://localhost:11434/api/chat', json=payload, stream=True)

        prompt = 'Simulate next physics iteration with provided objects'
        tick += 1

        # simulation
        balls = []

        for msg in req.iter_lines():
            data = json.loads(msg)
            balls = json.loads(data['message']['content'])
            messages.append({'role': 'assistant', 'content': json.dumps(balls)})
        print(f'tick {tick}: {balls}')


simulation = threading.Thread(target=simulate)
simulation.start()

# main loop
while running:
    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # render
    screen.fill((255, 255, 255))

    for ball in balls:
        pygame.draw.circle(screen, (0, 0, 0), (ball['x'], ball['y']), 30)

    pygame.display.flip()
    fps_limit.tick(10)

pygame.quit()
simulation.join()
