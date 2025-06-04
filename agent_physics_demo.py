import typing
import ollama
import pygame
import pydantic
import threading


class RigidBody(pydantic.BaseModel):
    x: float
    y: float
    vx: float
    vy: float


class World(pydantic.BaseModel):
    bodies: typing.List[RigidBody]


# main
pygame.init()

screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("LLM physics simulation")

model = 'qwen3:4b'
prompt = 'Generate 3 bodies with random velocity: in center of 640x480 and remaining in random place'
messages = []

tick = 0
running = True
fps_limit = pygame.time.Clock()

world = World(bodies=[])

# simulation thread
def simulate():
    global prompt
    global running
    global world
    global messages
    global tick

    while running:
        messages.append({'role': 'user', 'content': prompt})

        response = ollama.chat(
            model=model,
            messages=messages,
            format=World.model_json_schema()
        )

        # simulation
        world = World.model_validate_json(response.message.content)
        messages.append({'role': 'assistant', 'content': world.model_dump_json()})

        print(f'tick {tick}: {world.bodies}')

        prompt = 'Simulate next physics iteration with provided bodies'
        tick += 1


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

    for obj in world.bodies:
        pygame.draw.circle(screen, (0, 0, 0), (obj.x, obj.y), 30)

    pygame.display.flip()
    fps_limit.tick(1)

pygame.quit()
simulation.join()
