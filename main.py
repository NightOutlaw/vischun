import asyncio
import threading
import time
import webbrowser

from config_loader import ConfigLoader
from web_interface.app import app as web_app
from stream_client import stream_json_lines
from buffer import get_safe
from processor import process_iq_packet


def start_web_interface():
    web_app.run(debug=False, use_reloader=False, port=8050)


async def consume_stream(stream_id: str, queue: asyncio.Queue, config: dict):
    print(f"[🔁] Споживач для: {stream_id}")
    counter = 0
    while True:
        json_obj = await get_safe(queue, stream_id)
        process_iq_packet(json_obj, config, stream_id=stream_id)
        counter += 1
        if counter % 500 == 0:
            print(f"[{stream_id}] ✅ Оброблено {counter} IQ-пакетів")


async def main():
    cfg_loader = ConfigLoader("config.yaml")
    stream_names = cfg_loader.get_stream_names()
    tasks = []

    for stream_id in stream_names:
        config = cfg_loader.get_config_for_stream(stream_id)
        queue = asyncio.Queue()
        port = config.get("port", 55551)
        url = f"http://127.0.0.1:{port}/stream"
        tasks.append(stream_json_lines(stream_id, url, queue))
        tasks.append(consume_stream(stream_id, queue, config))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        threading.Thread(target=start_web_interface, daemon=True).start()
        time.sleep(1)
        webbrowser.open("http://localhost:8050")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[⛔] Зупинено вручну.")
