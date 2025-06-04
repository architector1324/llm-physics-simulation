import typing
import ollama
import pydantic


class RigidBody(pydantic.BaseModel):
    x: float
    y: float
    vx: float
    vy: float


class World(pydantic.BaseModel):
    bodies: typing.List[RigidBody]


# main
model = 'qwen3:4b'
prompt = 'Generate 3 bodies with random velocity: in center of 640x480 and remaining in random place'
messages = []

tick = 0

while True:
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
