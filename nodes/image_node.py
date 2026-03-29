from fal_client.client import FalClientHTTPError

from .fal_utils import ApiHandler, ImageUtils, ResultProcessor


class NanoBanana2EditNode:
    """Image editing using fal.ai's Nano Banana 2 Edit (Gemini Flash)."""

    CATEGORY = "fal.ai/Image"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2**31 - 1}),
                "aspect_ratio": (
                    [
                        "auto",
                        "21:9",
                        "16:9",
                        "3:2",
                        "4:3",
                        "5:4",
                        "1:1",
                        "4:5",
                        "3:4",
                        "2:3",
                        "9:16",
                    ],
                    {"default": "auto"},
                ),
                "resolution": (["0.5K", "1K", "2K", "4K"], {"default": "1K"}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
                "safety_tolerance": ("INT", {"default": 4, "min": 1, "max": 6}),
                "thinking_level": (["none", "minimal", "high"], {"default": "none"}),
                "enable_web_search": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "edit"

    def edit(
        self,
        image,
        prompt,
        num_images=1,
        seed=-1,
        aspect_ratio="auto",
        resolution="1K",
        output_format="png",
        safety_tolerance=4,
        thinking_level="none",
        enable_web_search=False,
    ):
        image_urls = ImageUtils.prepare_image_urls(image)

        arguments = {
            "prompt": prompt,
            "image_urls": image_urls,
            "num_images": num_images,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
            "output_format": output_format,
            "safety_tolerance": safety_tolerance,
            "enable_web_search": enable_web_search,
        }

        if seed != -1:
            arguments["seed"] = seed
        if thinking_level != "none":
            arguments["thinking_level"] = thinking_level

        try:
            result = ApiHandler.submit_and_get_result(
                "fal-ai/nano-banana-2/edit", arguments
            )
        except FalClientHTTPError as e:
            msg = _extract_fal_error_message(e)
            raise RuntimeError(f"fal.ai error: {msg}") from None
        return (ResultProcessor.process_image_result(result),)


def _extract_fal_error_message(e):
    """Pull a human-readable message from a FalClientHTTPError."""
    body = e.args[0] if e.args else None
    if isinstance(body, list) and body:
        entry = body[0]
        if isinstance(entry, dict):
            return entry.get("msg", str(e))
    return str(e)


NODE_CLASS_MAPPINGS = {
    "FAL_NanoBanana2Edit": NanoBanana2EditNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_NanoBanana2Edit": "Nano Banana 2 Edit (fal.ai)",
}
