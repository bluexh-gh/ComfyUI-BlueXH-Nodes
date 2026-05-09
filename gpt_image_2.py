import base64
import io
import logging
from typing import List

import numpy as np
import requests
import torch
from PIL import Image

logger = logging.getLogger(__name__)

CODE_SUCCESS = 0
CODE_FAILED = 1
CODE_TIMEOUT = 2
CODE_UNKNOWN = 999


def tensor_to_pil(image: torch.Tensor) -> Image.Image:
    return Image.fromarray(np.clip(255.0 * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))


def image_to_base64(pil_image: Image.Image) -> str:
    image_data = io.BytesIO()
    pil_image.save(image_data, format="PNG")
    image_data_bytes = image_data.getvalue()
    encoded_image = "data:image/png;base64," + base64.b64encode(image_data_bytes).decode("utf-8")
    return encoded_image


def base64_to_tensor(b64_data: str) -> torch.Tensor:
    img_bytes = base64.b64decode(b64_data)
    pil_image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img_array = np.array(pil_image).astype(np.float32) / 255.0
    return torch.from_numpy(img_array).unsqueeze(0)


class GptImage2:
    CATEGORY = "StarUnion-GptImage2"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url_prefix": (
                    "STRING",
                    {"default": "https://bmc-llm-relay.bluemediagroup.cn", "multiline": False},
                ),
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "timeout": (
                    "INT",
                    {
                        "default": 300,
                        "min": 1,
                        "max": 1800,
                        "step": 1,
                        "display": "number",
                    },
                ),
            },
            "optional": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
                "image6": ("IMAGE",),
                "image7": ("IMAGE",),
                "image8": ("IMAGE",),
                "image9": ("IMAGE",),
                "image10": ("IMAGE",),
                "size": (
                    ["auto", "1024x1024", "1536x1024", "1024x1536"],
                    {"default": "auto"},
                ),
                "quality": (
                    ["auto", "low", "medium", "high"],
                    {"default": "auto"},
                ),
                "output_format": (
                    ["png", "jpeg", "webp"],
                    {"default": "png"},
                ),
            },
        }

    OUTPUT_NODE = True
    RETURN_TYPES = ("INT", "STRING", "IMAGE")
    RETURN_NAMES = ("code", "message", "image")
    FUNCTION = "generate_image"

    def generate_image(
        self,
        url_prefix: str,
        api_key: str,
        prompt: str,
        timeout: int,
        image1=None,
        image2=None,
        image3=None,
        image4=None,
        image5=None,
        image6=None,
        image7=None,
        image8=None,
        image9=None,
        image10=None,
        size: str = "auto",
        quality: str = "auto",
        output_format: str = "png",
    ):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            image_inputs = [image1, image2, image3, image4, image5, image6, image7, image8, image9, image10]
            image_data_uris = self._convert_images_to_data_uris(image_inputs)

            if image_data_uris:
                logger.info(f"GptImage2: Calling edit API with {len(image_data_uris)} images")
                return self._call_edit_api(
                    url_prefix, headers, prompt, image_data_uris, size,
                    quality, output_format, timeout
                )
            else:
                logger.info("GptImage2: Calling generation API")
                return self._call_generation_api(
                    url_prefix, headers, prompt, size,
                    quality, output_format, timeout
                )
        except requests.exceptions.Timeout:
            logger.warning(f"GptImage2: Request timeout after {timeout}s")
            return (CODE_TIMEOUT, f"Request timeout after {timeout}s", torch.zeros(1, 1, 1, 3))
        except Exception as err:
            logger.warning(f"GptImage2: Unknown error during image generation: {err}")
            return (CODE_UNKNOWN, f"Unknown error during image generation: {err}", torch.zeros(1, 1, 1, 3))

    def _convert_images_to_data_uris(self, images: List) -> List[str]:
        data_uris = []
        for img in images:
            if img is None:
                continue
            if isinstance(img, torch.Tensor) and img.numel() > 0 and img.dim() >= 3:
                pil_image = tensor_to_pil(img)
                data_uri = image_to_base64(pil_image)
                data_uris.append(data_uri)
        return data_uris

    def _call_generation_api(
        self,
        url_prefix: str,
        headers: dict,
        prompt: str,
        size: str,
        quality: str,
        output_format: str,
        timeout: int,
    ):
        url = f"{url_prefix}/v1/images/generations"
        body = {
            "model": "gpt-image-2",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "background": "auto",
            "output_format": output_format,
            "n": 1,
        }

        response = requests.post(url=url, json=body, headers=headers, timeout=timeout)
        return self._parse_response(response)

    def _call_edit_api(
        self,
        url_prefix: str,
        headers: dict,
        prompt: str,
        image_data_uris: List[str],
        size: str,
        quality: str,
        output_format: str,
        timeout: int,
    ):
        url = f"{url_prefix}/v1/images/edits"

        auth_headers = {"Authorization": headers["Authorization"]}

        data = {
            "model": "gpt-image-2",
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "background": "auto",
            "output_format": output_format,
            "n": 1,
            "input_fidelity": "high",
        }

        files = []
        for i, data_uri in enumerate(image_data_uris):
            if data_uri.startswith("data:image/png;base64,"):
                b64_data = data_uri.split(",", 1)[1]
                img_bytes = base64.b64decode(b64_data)
                files.append(("image[]", (f"image{i}.png", io.BytesIO(img_bytes), "image/png")))

        response = requests.post(url=url, data=data, files=files, headers=auth_headers, timeout=timeout)
        return self._parse_response(response)

    def _parse_response(self, response: requests.Response):
        empty_image = torch.zeros(1, 1, 1, 3)

        if response.status_code != 200:
            logger.warning(f"GptImage2: API request failed, status: {response.status_code}")
            return (CODE_FAILED, f"API request failed, status: {response.status_code}, response: {response.text}", empty_image)

        try:
            response_data = response.json()
        except requests.exceptions.JSONDecodeError as e:
            logger.warning(f"GptImage2: Invalid JSON response: {e}")
            return (CODE_FAILED, f"Invalid JSON response: {e}", empty_image)

        if "error" in response_data:
            error_msg = response_data.get("error", {}).get("message", "Unknown error")
            logger.warning(f"GptImage2: API returned error: {error_msg}")
            return (CODE_FAILED, f"API returned error: {error_msg}", empty_image)

        data = response_data.get("data", [])
        if not data:
            logger.warning("GptImage2: API returned empty data")
            return (CODE_FAILED, "API returned empty data", empty_image)

        image_base64 = data[0].get("b64_json", "")
        if not image_base64:
            logger.warning("GptImage2: API returned empty image data")
            return (CODE_FAILED, "API returned empty image data", empty_image)

        image_tensor = base64_to_tensor(image_base64)
        logger.info(f"GptImage2: Image generated successfully, shape: {image_tensor.shape}")
        return (CODE_SUCCESS, "Image generated successfully", image_tensor)
