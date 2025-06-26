import yaml
import os

class ConfigLoader:
    """
    Завантажує конфігурацію з YAML і надає доступ до параметрів для потоків.
    """

    def __init__(self, path="config.yaml"):
        if not os.path.exists(path):
            raise FileNotFoundError(f"❌ Конфігураційний файл не знайдено: {path}")
        with open(path, "r", encoding="utf-8") as f:
            self.full_config = yaml.safe_load(f)

        if "streams" not in self.full_config:
            raise ValueError("⚠️ Невірна структура config.yaml: відсутній блок 'streams'")

    def get_stream_names(self):
        """Повертає список усіх доступних потоків."""
        return list(self.full_config["streams"].keys())

    def get_config_for_stream(self, stream_name):
        """Повертає конфігурацію для заданого потоку."""
        return self.full_config["streams"].get(stream_name)

    def get_module_config(self, stream_name, module_name):
        """
        Повертає параметри аналітичного модуля для конкретного потоку.
        Наприклад: get_module_config("Потік-2", "burst_detector")
        """
        stream_cfg = self.get_config_for_stream(stream_name)
        if not stream_cfg:
            raise KeyError(f"❌ Потік '{stream_name}' не знайдено в конфігурації.")
        return stream_cfg.get(module_name, {})