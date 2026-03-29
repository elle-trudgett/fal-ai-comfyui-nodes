# ComfyUI fal.ai Nodes

Custom [ComfyUI](https://www.comfy.org/) nodes for [fal.ai](https://fal.ai/) image generation and editing models.

## Nodes

| Node | Description | Endpoint |
|---|---|---|
| **Nano Banana 2** | Text-to-image generation | `fal-ai/nano-banana-2` |
| **Nano Banana 2 Edit** | Image editing with text prompts | `fal-ai/nano-banana-2/edit` |
| **Nano Banana Pro** | Text-to-image generation (Pro) | `fal-ai/nano-banana-pro` |
| **Nano Banana Pro Edit** | Image editing with text prompts (Pro) | `fal-ai/nano-banana-pro/edit` |

All nodes appear under the **fal.ai/Image** category in ComfyUI.

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
