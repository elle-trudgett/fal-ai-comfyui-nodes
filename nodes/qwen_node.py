from fal_client.client import FalClientHTTPError

from .fal_utils import ApiHandler, ImageUtils, ResultProcessor, extract_fal_error_message

IMAGE_SIZE_PRESETS = [
    "square_hd",
    "square",
    "portrait_4_3",
    "portrait_16_9",
    "landscape_4_3",
    "landscape_16_9",
    "custom",
]


class QwenImageNode:
    """Text-to-image generation using fal.ai's Qwen Image."""

    CATEGORY = "fal.ai/Image"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "image_size": (IMAGE_SIZE_PRESETS, {"default": "landscape_4_3"}),
                "custom_width": ("INT", {"default": 1024, "min": 64, "max": 14142}),
                "custom_height": ("INT", {"default": 768, "min": 64, "max": 14142}),
                "num_inference_steps": ("INT", {"default": 30, "min": 2, "max": 250}),
                "guidance_scale": ("FLOAT", {"default": 2.5, "min": 0.0, "max": 20.0, "step": 0.1}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2**31 - 1}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "output_format": (["png", "jpeg"], {"default": "png"}),
                "acceleration": (["none", "regular", "high"], {"default": "none"}),
                "use_turbo": ("BOOLEAN", {"default": False}),
                "enable_safety_checker": ("BOOLEAN", {"default": True}),
                "sync_mode": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"

    def generate(
        self,
        prompt,
        num_images=1,
        image_size="landscape_4_3",
        custom_width=1024,
        custom_height=768,
        num_inference_steps=30,
        guidance_scale=2.5,
        seed=-1,
        negative_prompt="",
        output_format="png",
        acceleration="none",
        use_turbo=False,
        enable_safety_checker=True,
        sync_mode=False,
    ):
        if image_size == "custom":
            size = {"width": custom_width, "height": custom_height}
        else:
            size = image_size

        arguments = {
            "prompt": prompt,
            "num_images": num_images,
            "image_size": size,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "output_format": output_format,
            "acceleration": acceleration,
            "use_turbo": use_turbo,
            "enable_safety_checker": enable_safety_checker,
            "sync_mode": sync_mode,
        }

        if seed != -1:
            arguments["seed"] = seed
        if negative_prompt:
            arguments["negative_prompt"] = negative_prompt

        try:
            result = ApiHandler.submit_and_get_result(
                "fal-ai/qwen-image", arguments
            )
        except FalClientHTTPError as e:
            msg = extract_fal_error_message(e)
            raise RuntimeError(f"fal.ai error: {msg}") from None
        return (ResultProcessor.process_image_result(result),)


class QwenImageToImageNode:
    """Image-to-image generation using fal.ai's Qwen Image."""

    CATEGORY = "fal.ai/Image"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "strength": ("FLOAT", {"default": 0.6, "min": 0.0, "max": 1.0, "step": 0.05}),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "image_size": (IMAGE_SIZE_PRESETS, {"default": "landscape_4_3"}),
                "custom_width": ("INT", {"default": 1024, "min": 64, "max": 14142}),
                "custom_height": ("INT", {"default": 768, "min": 64, "max": 14142}),
                "num_inference_steps": ("INT", {"default": 30, "min": 2, "max": 250}),
                "guidance_scale": ("FLOAT", {"default": 2.5, "min": 0.0, "max": 20.0, "step": 0.1}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2**31 - 1}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "output_format": (["png", "jpeg"], {"default": "png"}),
                "acceleration": (["none", "regular", "high"], {"default": "none"}),
                "use_turbo": ("BOOLEAN", {"default": False}),
                "enable_safety_checker": ("BOOLEAN", {"default": True}),
                "sync_mode": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"

    def generate(
        self,
        image,
        prompt,
        strength=0.6,
        num_images=1,
        image_size="landscape_4_3",
        custom_width=1024,
        custom_height=768,
        num_inference_steps=30,
        guidance_scale=2.5,
        seed=-1,
        negative_prompt="",
        output_format="png",
        acceleration="none",
        use_turbo=False,
        enable_safety_checker=True,
        sync_mode=False,
    ):
        image_url = ImageUtils.upload_image(image)

        if image_size == "custom":
            size = {"width": custom_width, "height": custom_height}
        else:
            size = image_size

        arguments = {
            "prompt": prompt,
            "image_url": image_url,
            "strength": strength,
            "num_images": num_images,
            "image_size": size,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "output_format": output_format,
            "acceleration": acceleration,
            "use_turbo": use_turbo,
            "enable_safety_checker": enable_safety_checker,
            "sync_mode": sync_mode,
        }

        if seed != -1:
            arguments["seed"] = seed
        if negative_prompt:
            arguments["negative_prompt"] = negative_prompt

        try:
            result = ApiHandler.submit_and_get_result(
                "fal-ai/qwen-image/image-to-image", arguments
            )
        except FalClientHTTPError as e:
            msg = extract_fal_error_message(e)
            raise RuntimeError(f"fal.ai error: {msg}") from None
        return (ResultProcessor.process_image_result(result),)


class QwenImageEditNode:
    """Image editing using fal.ai's Qwen Image Edit 2511."""

    CATEGORY = "fal.ai/Image"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "image_size": (IMAGE_SIZE_PRESETS, {"default": "landscape_4_3"}),
                "custom_width": ("INT", {"default": 1024, "min": 64, "max": 14142}),
                "custom_height": ("INT", {"default": 768, "min": 64, "max": 14142}),
                "num_inference_steps": ("INT", {"default": 28, "min": 1, "max": 50}),
                "guidance_scale": ("FLOAT", {"default": 4.5, "min": 1.0, "max": 20.0, "step": 0.1}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2**31 - 1}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
                "acceleration": (["none", "regular", "high"], {"default": "regular"}),
                "enable_safety_checker": ("BOOLEAN", {"default": True}),
                "sync_mode": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "edit"

    def edit(
        self,
        image,
        prompt,
        image2=None,
        image3=None,
        num_images=1,
        image_size="landscape_4_3",
        custom_width=1024,
        custom_height=768,
        num_inference_steps=28,
        guidance_scale=4.5,
        seed=-1,
        negative_prompt="",
        output_format="png",
        acceleration="regular",
        enable_safety_checker=True,
        sync_mode=False,
    ):
        image_urls = ImageUtils.collect_image_urls(image, image2, image3)

        if image_size == "custom":
            size = {"width": custom_width, "height": custom_height}
        else:
            size = image_size

        arguments = {
            "prompt": prompt,
            "image_urls": image_urls,
            "num_images": num_images,
            "image_size": size,
            "num_inference_steps": num_inference_steps,
            "guidance_scale": guidance_scale,
            "output_format": output_format,
            "acceleration": acceleration,
            "enable_safety_checker": enable_safety_checker,
            "sync_mode": sync_mode,
        }

        if seed != -1:
            arguments["seed"] = seed
        if negative_prompt:
            arguments["negative_prompt"] = negative_prompt

        try:
            result = ApiHandler.submit_and_get_result(
                "fal-ai/qwen-image-edit-2511", arguments
            )
        except FalClientHTTPError as e:
            msg = extract_fal_error_message(e)
            raise RuntimeError(f"fal.ai error: {msg}") from None
        return (ResultProcessor.process_image_result(result),)


class QwenImage2Node:
    """Text-to-image generation using fal.ai's Qwen Image 2."""

    CATEGORY = "fal.ai/Image"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "image_size": (IMAGE_SIZE_PRESETS, {"default": "square_hd"}),
                "custom_width": ("INT", {"default": 1024, "min": 512, "max": 2048}),
                "custom_height": ("INT", {"default": 1024, "min": 512, "max": 2048}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2**31 - 1}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
                "enable_prompt_expansion": ("BOOLEAN", {"default": True}),
                "enable_safety_checker": ("BOOLEAN", {"default": True}),
                "sync_mode": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"

    def generate(
        self,
        prompt,
        num_images=1,
        image_size="square_hd",
        custom_width=1024,
        custom_height=1024,
        seed=-1,
        negative_prompt="",
        output_format="png",
        enable_prompt_expansion=True,
        enable_safety_checker=True,
        sync_mode=False,
    ):
        if image_size == "custom":
            size = {"width": custom_width, "height": custom_height}
        else:
            size = image_size

        arguments = {
            "prompt": prompt,
            "num_images": num_images,
            "image_size": size,
            "output_format": output_format,
            "enable_prompt_expansion": enable_prompt_expansion,
            "enable_safety_checker": enable_safety_checker,
            "sync_mode": sync_mode,
        }

        if seed != -1:
            arguments["seed"] = seed
        if negative_prompt:
            arguments["negative_prompt"] = negative_prompt

        try:
            result = ApiHandler.submit_and_get_result(
                "fal-ai/qwen-image-2/text-to-image", arguments
            )
        except FalClientHTTPError as e:
            msg = extract_fal_error_message(e)
            raise RuntimeError(f"fal.ai error: {msg}") from None
        return (ResultProcessor.process_image_result(result),)


class QwenImage2EditNode:
    """Image editing using fal.ai's Qwen Image 2 Edit."""

    CATEGORY = "fal.ai/Image"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 6}),
                "image_size": (IMAGE_SIZE_PRESETS, {"default": "square_hd"}),
                "custom_width": ("INT", {"default": 1024, "min": 512, "max": 2048}),
                "custom_height": ("INT", {"default": 1024, "min": 512, "max": 2048}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2**31 - 1}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
                "enable_prompt_expansion": ("BOOLEAN", {"default": True}),
                "enable_safety_checker": ("BOOLEAN", {"default": True}),
                "sync_mode": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "edit"

    def edit(
        self,
        image,
        prompt,
        image2=None,
        image3=None,
        num_images=1,
        image_size="square_hd",
        custom_width=1024,
        custom_height=1024,
        seed=-1,
        negative_prompt="",
        output_format="png",
        enable_prompt_expansion=True,
        enable_safety_checker=True,
        sync_mode=False,
    ):
        image_urls = ImageUtils.collect_image_urls(image, image2, image3)

        if image_size == "custom":
            size = {"width": custom_width, "height": custom_height}
        else:
            size = image_size

        arguments = {
            "prompt": prompt,
            "image_urls": image_urls,
            "num_images": num_images,
            "image_size": size,
            "output_format": output_format,
            "enable_prompt_expansion": enable_prompt_expansion,
            "enable_safety_checker": enable_safety_checker,
            "sync_mode": sync_mode,
        }

        if seed != -1:
            arguments["seed"] = seed
        if negative_prompt:
            arguments["negative_prompt"] = negative_prompt

        try:
            result = ApiHandler.submit_and_get_result(
                "fal-ai/qwen-image-2/edit", arguments
            )
        except FalClientHTTPError as e:
            msg = extract_fal_error_message(e)
            raise RuntimeError(f"fal.ai error: {msg}") from None
        return (ResultProcessor.process_image_result(result),)


class QwenImage2ProNode:
    """Text-to-image generation using fal.ai's Qwen Image 2 Pro."""

    CATEGORY = "fal.ai/Image"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "num_images": ("INT", {"default": 1, "min": 1, "max": 4}),
                "image_size": (IMAGE_SIZE_PRESETS, {"default": "square_hd"}),
                "custom_width": ("INT", {"default": 1024, "min": 512, "max": 2048}),
                "custom_height": ("INT", {"default": 1024, "min": 512, "max": 2048}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2**31 - 1}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
                "enable_prompt_expansion": ("BOOLEAN", {"default": True}),
                "enable_safety_checker": ("BOOLEAN", {"default": True}),
                "sync_mode": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate"

    def generate(
        self,
        prompt,
        num_images=1,
        image_size="square_hd",
        custom_width=1024,
        custom_height=1024,
        seed=-1,
        negative_prompt="",
        output_format="png",
        enable_prompt_expansion=True,
        enable_safety_checker=True,
        sync_mode=False,
    ):
        if image_size == "custom":
            size = {"width": custom_width, "height": custom_height}
        else:
            size = image_size

        arguments = {
            "prompt": prompt,
            "num_images": num_images,
            "image_size": size,
            "output_format": output_format,
            "enable_prompt_expansion": enable_prompt_expansion,
            "enable_safety_checker": enable_safety_checker,
            "sync_mode": sync_mode,
        }

        if seed != -1:
            arguments["seed"] = seed
        if negative_prompt:
            arguments["negative_prompt"] = negative_prompt

        try:
            result = ApiHandler.submit_and_get_result(
                "fal-ai/qwen-image-2/pro/text-to-image", arguments
            )
        except FalClientHTTPError as e:
            msg = extract_fal_error_message(e)
            raise RuntimeError(f"fal.ai error: {msg}") from None
        return (ResultProcessor.process_image_result(result),)


class QwenImage2ProEditNode:
    """Image editing using fal.ai's Qwen Image 2 Pro Edit."""

    CATEGORY = "fal.ai/Image"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "prompt": ("STRING", {"default": "", "multiline": True}),
            },
            "optional": {
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "num_images": ("INT", {"default": 1, "min": 1, "max": 6}),
                "image_size": (IMAGE_SIZE_PRESETS, {"default": "square_hd"}),
                "custom_width": ("INT", {"default": 1024, "min": 512, "max": 2048}),
                "custom_height": ("INT", {"default": 1024, "min": 512, "max": 2048}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 2**31 - 1}),
                "negative_prompt": ("STRING", {"default": "", "multiline": True}),
                "output_format": (["png", "jpeg", "webp"], {"default": "png"}),
                "enable_prompt_expansion": ("BOOLEAN", {"default": True}),
                "enable_safety_checker": ("BOOLEAN", {"default": True}),
                "sync_mode": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "edit"

    def edit(
        self,
        image,
        prompt,
        image2=None,
        image3=None,
        num_images=1,
        image_size="square_hd",
        custom_width=1024,
        custom_height=1024,
        seed=-1,
        negative_prompt="",
        output_format="png",
        enable_prompt_expansion=True,
        enable_safety_checker=True,
        sync_mode=False,
    ):
        image_urls = ImageUtils.collect_image_urls(image, image2, image3)

        if image_size == "custom":
            size = {"width": custom_width, "height": custom_height}
        else:
            size = image_size

        arguments = {
            "prompt": prompt,
            "image_urls": image_urls,
            "num_images": num_images,
            "image_size": size,
            "output_format": output_format,
            "enable_prompt_expansion": enable_prompt_expansion,
            "enable_safety_checker": enable_safety_checker,
            "sync_mode": sync_mode,
        }

        if seed != -1:
            arguments["seed"] = seed
        if negative_prompt:
            arguments["negative_prompt"] = negative_prompt

        try:
            result = ApiHandler.submit_and_get_result(
                "fal-ai/qwen-image-2/pro/edit", arguments
            )
        except FalClientHTTPError as e:
            msg = extract_fal_error_message(e)
            raise RuntimeError(f"fal.ai error: {msg}") from None
        return (ResultProcessor.process_image_result(result),)


NODE_CLASS_MAPPINGS = {
    "FAL_QwenImage": QwenImageNode,
    "FAL_QwenImageToImage": QwenImageToImageNode,
    "FAL_QwenImageEdit": QwenImageEditNode,
    "FAL_QwenImage2": QwenImage2Node,
    "FAL_QwenImage2Edit": QwenImage2EditNode,
    "FAL_QwenImage2Pro": QwenImage2ProNode,
    "FAL_QwenImage2ProEdit": QwenImage2ProEditNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FAL_QwenImage": "Qwen Image (fal.ai)",
    "FAL_QwenImageToImage": "Qwen Image-to-Image (fal.ai)",
    "FAL_QwenImageEdit": "Qwen Image Edit (fal.ai)",
    "FAL_QwenImage2": "Qwen Image 2 (fal.ai)",
    "FAL_QwenImage2Edit": "Qwen Image 2 Edit (fal.ai)",
    "FAL_QwenImage2Pro": "Qwen Image 2 Pro (fal.ai)",
    "FAL_QwenImage2ProEdit": "Qwen Image 2 Pro Edit (fal.ai)",
}
