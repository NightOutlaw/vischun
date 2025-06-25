import asyncio

MAX_BUFFER_SIZE = 10_000


# Створюємо черги з обмеженим розміром
def init_buffers(port_count: int):
    return {
        f"Потік-{i+1}": asyncio.Queue(maxsize=MAX_BUFFER_SIZE)
        for i in range(port_count)
    }


# Додавання з контролем переповнення
def put_safe(queue: asyncio.Queue, obj, name: str):
    if queue.full():
        _ = queue.get_nowait()
        print(f"[{name}] ⚠️ Буфер повний. Видалено найстаріший об'єкт.")
    queue.put_nowait(obj)


# Отримання з контролем виключень
async def get_safe(queue: asyncio.Queue, name: str):
    try:
        return await queue.get()
    except Exception as e:
        print(f"[{name}] ❌ Помилка під час читання з буфера: {e}")
        return None
