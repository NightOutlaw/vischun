import httpx
import json
from buffer import put_safe


async def stream_json_lines(name: str, url: str, queue):
    count = 0
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            async with client.stream("GET", url) as response:
                print(f"[{name}] 🔗 Підключено до {url} | Статус: {response.status_code}")
                async for line in response.aiter_lines():
                    clean_line = line.strip().replace('\x1e', '')
                    if not clean_line:
                        continue
                    try:
                        obj = json.loads(clean_line)
                        put_safe(queue, obj, name)
                        count += 1
                        if count % 1000 == 0:
                            print(f"[{name}] ✔ Отримано {count} JSON | Буфер: {queue.qsize()}")
                    except json.JSONDecodeError as e:
                        print(f"[{name}] ⚠️ JSON-помилка: {e}")
        except httpx.HTTPError as e:
            print(f"[{name}] 💥 HTTP помилка: {e}")
