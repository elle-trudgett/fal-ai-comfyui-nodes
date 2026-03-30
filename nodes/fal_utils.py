import configparser
import io
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import torch
from PIL import Image

import fal_client as fal

CONFIG_PATH = Path(__file__).parent.parent / "config.ini"


class FalConfig:
    """Singleton managing fal.ai API credentials."""

    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            api_key = os.getenv("FAL_KEY", "")
            if not api_key:
                api_key = cls._read_config_key()
            if not api_key:
                raise ValueError(
                    "FAL_KEY not set. Set the FAL_KEY environment variable "
                    "or add it to config.ini."
                )
            os.environ["FAL_KEY"] = api_key
            cls._client = fal
        return cls._client

    @classmethod
    def _read_config_key(cls):
        if not CONFIG_PATH.exists():
            return ""
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        key = config.get("API", "FAL_KEY", fallback="")
        if key.startswith("<") and key.endswith(">"):
            return ""
        return key


class ImageUtils:
    @staticmethod
    def tensor_to_pil(image_tensor):
        """Convert a single HxWxC float tensor (0-1) to a PIL Image."""
        if image_tensor.dim() == 4:
            image_tensor = image_tensor[0]
        arr = (image_tensor.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        return Image.fromarray(arr)

    @staticmethod
    def upload_image(image_tensor):
        """Upload an image tensor to fal and return the URL."""
        FalConfig.get_client()
        pil_image = ImageUtils.tensor_to_pil(image_tensor)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            pil_image.save(f, format="PNG")
            tmp_path = f.name
        try:
            url = fal.upload_file(tmp_path)
        finally:
            os.unlink(tmp_path)
        return url

    @staticmethod
    def prepare_image_urls(image_tensor):
        """Upload batch of images and return list of URLs."""
        if image_tensor.dim() == 3:
            return [ImageUtils.upload_image(image_tensor)]
        urls = []
        for i in range(image_tensor.shape[0]):
            urls.append(ImageUtils.upload_image(image_tensor[i]))
        return urls


class ResultProcessor:
    @staticmethod
    def process_image_result(result):
        """Download images from result URLs and return as tensor batch."""
        import urllib.request

        images = result.get("images", [])
        if not images:
            raise ValueError("No images returned from API")

        tensors = []
        for img_data in images:
            url = img_data["url"]
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as resp:
                data = resp.read()

            pil_image = Image.open(io.BytesIO(data)).convert("RGB")
            arr = np.array(pil_image).astype(np.float32) / 255.0
            tensors.append(torch.from_numpy(arr))

        return torch.stack(tensors)


def extract_fal_error_message(e):
    """Pull a human-readable message from a FalClientHTTPError."""
    body = e.args[0] if e.args else None
    if isinstance(body, list) and body:
        entry = body[0]
        if isinstance(entry, dict):
            return entry.get("msg", str(e))
    return str(e)


class ApiHandler:
    @staticmethod
    def submit_and_get_result(endpoint, arguments):
        """Submit a request to fal.ai and return the result."""
        client = FalConfig.get_client()
        result = client.subscribe(endpoint, arguments=arguments)
        return result

    @staticmethod
    def submit_multiple_and_get_results(endpoint, variations):
        """Submit multiple requests concurrently."""
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(ApiHandler.submit_and_get_result, endpoint, args)
                for args in variations
            ]
            return [f.result() for f in futures]
