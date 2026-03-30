# ComfyUI fal.ai Nodes

Custom [ComfyUI](https://www.comfy.org/) nodes for [fal.ai](https://fal.ai/) image generation and editing models.

## Nodes

All nodes appear under the **fal.ai/Image** category in ComfyUI.

### Nano Banana

| Node | Description | Endpoint |
|---|---|---|
| **Nano Banana 2** | Text-to-image generation | `fal-ai/nano-banana-2` |
| **Nano Banana 2 Edit** | Image editing with text prompts | `fal-ai/nano-banana-2/edit` |
| **Nano Banana Pro** | Text-to-image generation (Pro) | `fal-ai/nano-banana-pro` |
| **Nano Banana Pro Edit** | Image editing with text prompts (Pro) | `fal-ai/nano-banana-pro/edit` |

### Qwen Image

| Node | Description | Endpoint |
|---|---|---|
| **Qwen Image** | Text-to-image generation | `fal-ai/qwen-image` |
| **Qwen Image-to-Image** | Image-to-image with strength control | `fal-ai/qwen-image/image-to-image` |
| **Qwen Image Edit** | Prompt-guided image editing | `fal-ai/qwen-image-edit-2511` |
| **Qwen Image 2** | Text-to-image generation (v2) | `fal-ai/qwen-image-2/text-to-image` |
| **Qwen Image 2 Edit** | Image editing (v2) | `fal-ai/qwen-image-2/edit` |
| **Qwen Image 2 Pro** | Text-to-image generation (v2 Pro) | `fal-ai/qwen-image-2/pro/text-to-image` |
| **Qwen Image 2 Pro Edit** | Image editing (v2 Pro) | `fal-ai/qwen-image-2/pro/edit` |

## Installation

Clone into your ComfyUI `custom_nodes` directory:

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/elle-trudgett/fal-ai-comfyui-nodes.git
pip install -r fal-ai-comfyui-nodes/requirements.txt
```

## Configuration

Set your fal.ai API key using **one** of these methods:

1. **Environment variable** (recommended):
   ```bash
   export FAL_KEY="your-api-key"
   ```

2. **config.ini** (useful for ComfyUI Desktop):
   Create a `config.ini` file in the node package directory:
   ```ini
   [API]
   FAL_KEY = your-api-key
   ```

Get your API key at [fal.ai/dashboard/keys](https://fal.ai/dashboard/keys).

## License

MIT
