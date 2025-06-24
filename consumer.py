import asyncio
from processor import process_iq_packet


async def consume_stream(name: str, queue: asyncio.Queue, processor_fn=process_iq_packet):
    counter = 0
    while True:
        obj = await queue.get()
        counter += 1
        # Передача об'єкта на обробку
        processor_fn(obj)

        if counter % 1000 == 0:
            print(f"[{name}] ✅ Оброблено {counter} обʼєктів")