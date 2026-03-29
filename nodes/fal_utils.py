import io
import os
import struct
import zlib
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch

import fal_client as fal


class FalConfig:
    """Singleton managing fal.ai API credentials."""

    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            api_key = os.getenv("FAL_KEY", "")
            if not api_key:
                raise ValueError(
                    "FAL_KEY not set. Set the FAL_KEY environment variable."
                )
            cls._client = fal
        return cls._client


class ImageUtils:
    @staticmethod
    def tensor_to_png_bytes(image_tensor):
        """Convert a single HxWxC float tensor (0-1) to PNG bytes without PIL."""
        if image_tensor.dim() == 4:
            image_tensor = image_tensor[0]
        arr = (image_tensor.cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
        h, w, c = arr.shape

        def make_png(pixels, width, height):
            def chunk(chunk_type, data):
                c = chunk_type + data
                return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)

            header = b"\x89PNG\r\n\x1a\n"
            ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
            raw = b""
            for y in range(height):
                raw += b"\x00" + pixels[y * width * 3 : (y + 1) * width * 3]
            return header + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")

        if c == 3:
            pixels = arr.tobytes()
        else:
            pixels = arr[:, :, :3].tobytes()
        return make_png(pixels, w, h)

    @staticmethod
    def upload_image(image_tensor):
        """Upload an image tensor to fal and return the URL."""
        png_bytes = ImageUtils.tensor_to_png_bytes(image_tensor)
        url = fal.upload(png_bytes, content_type="image/png")
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

            arr = _decode_image_bytes(data)
            tensor = torch.from_numpy(arr.astype(np.float32) / 255.0)
            if tensor.dim() == 2:
                tensor = tensor.unsqueeze(-1).repeat(1, 1, 3)
            elif tensor.shape[-1] == 4:
                tensor = tensor[:, :, :3]
            tensors.append(tensor)

        return torch.stack(tensors)


def _decode_image_bytes(data):
    """Decode PNG/JPEG bytes to numpy array without PIL."""
    # Try PNG first
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return _decode_png(data)
    # Try JPEG via a temp approach - fall back to urllib + base64
    # For robustness, we'll use a simple approach
    try:
        return _decode_png(data)
    except Exception:
        pass

    # Fallback: try to use PIL if available
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(data)).convert("RGB")
        return np.array(img)
    except ImportError:
        raise RuntimeError(
            "Could not decode image. Install Pillow: pip install Pillow"
        )


def _decode_png(data):
    """Minimal PNG decoder."""
    import struct
    import zlib

    pos = 8  # skip signature
    ihdr = None
    idat_chunks = []

    while pos < len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        chunk_type = data[pos + 4 : pos + 8]
        chunk_data = data[pos + 8 : pos + 8 + length]
        pos += 12 + length

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(
                ">IIBB", chunk_data[:10]
            )
            ihdr = (width, height, bit_depth, color_type)
        elif chunk_type == b"IDAT":
            idat_chunks.append(chunk_data)
        elif chunk_type == b"IEND":
            break

    if ihdr is None:
        raise ValueError("Invalid PNG: no IHDR")

    width, height, bit_depth, color_type = ihdr
    raw = zlib.decompress(b"".join(idat_chunks))

    if color_type == 2:  # RGB
        channels = 3
    elif color_type == 6:  # RGBA
        channels = 4
    elif color_type == 0:  # Grayscale
        channels = 1
    else:
        raise ValueError(f"Unsupported PNG color type: {color_type}")

    stride = width * channels + 1  # +1 for filter byte
    pixels = bytearray(height * width * channels)

    prev_row = bytes(width * channels)
    for y in range(height):
        row_start = y * stride
        filter_byte = raw[row_start]
        row_data = bytearray(raw[row_start + 1 : row_start + stride])

        if filter_byte == 0:  # None
            pass
        elif filter_byte == 1:  # Sub
            for i in range(channels, len(row_data)):
                row_data[i] = (row_data[i] + row_data[i - channels]) & 0xFF
        elif filter_byte == 2:  # Up
            for i in range(len(row_data)):
                row_data[i] = (row_data[i] + prev_row[i]) & 0xFF
        elif filter_byte == 3:  # Average
            for i in range(len(row_data)):
                left = row_data[i - channels] if i >= channels else 0
                row_data[i] = (row_data[i] + (left + prev_row[i]) // 2) & 0xFF
        elif filter_byte == 4:  # Paeth
            for i in range(len(row_data)):
                left = row_data[i - channels] if i >= channels else 0
                up = prev_row[i]
                up_left = prev_row[i - channels] if i >= channels else 0
                p = left + up - up_left
                pa, pb, pc = abs(p - left), abs(p - up), abs(p - up_left)
                if pa <= pb and pa <= pc:
                    pr = left
                elif pb <= pc:
                    pr = up
                else:
                    pr = up_left
                row_data[i] = (row_data[i] + pr) & 0xFF

        offset = y * width * channels
        pixels[offset : offset + width * channels] = row_data
        prev_row = bytes(row_data)

    arr = np.frombuffer(bytes(pixels), dtype=np.uint8).reshape(height, width, channels)
    if channels == 1:
        arr = np.repeat(arr, 3, axis=2)
    return arr


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
