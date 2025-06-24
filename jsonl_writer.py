import asyncio
import json
from pathlib import Path

async def write_jsonl_batches(name: str, queue: asyncio.Queue, batch_size=10, out_dir="jsonl_dumps"):
    counter = 0
    Path(out_dir).mkdir(exist_ok=True)

    file_path = Path(out_dir) / f"{name.lower().replace(' ', '_')}.jsonl"
    buffer = []

    while True:
        try:
            obj = await queue.get()
            buffer.append(obj)
            if len(buffer) >= batch_size:
                # ⏳ Запис партії в файл
                with open(file_path, "a", encoding="utf-8") as f:
                    for entry in buffer:
                        f.write(json.dumps(entry) + "\n")
                counter += len(buffer)
                print(f"[{name}] 💾 Записано {len(buffer)} об’єктів | Всього: {counter}")
                buffer.clear()
        except Exception as e:
            print(f"[{name}] ⚠️ Помилка при записі: {e}")