from .gpt_image_2 import GptImage2

NODE_CLASS_MAPPINGS = {
    "GptImage2": GptImage2,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GptImage2": "GPT Image 2",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
