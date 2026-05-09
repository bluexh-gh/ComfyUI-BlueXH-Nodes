# ComfyUI-BlueXH-Nodes

ComfyUI custom nodes for HTTP requests and API integrations.

## Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/bluexh-gh/ComfyUI-BlueXH-Nodes.git
```

Restart ComfyUI after installation.

## Nodes

### GPT Image 2

Generate and edit images using GPT Image 2 API (OpenAI-compatible).

**Inputs:**
| Name | Type | Description |
|------|------|-------------|
| url_prefix | STRING | API endpoint URL |
| api_key | STRING | API key |
| prompt | STRING | Image generation prompt |
| timeout | INT | Request timeout in seconds |
| image1-10 | IMAGE | Optional reference images for editing |
| size | COMBO | Output size (auto, 1024x1024, etc.) |
| quality | COMBO | Image quality (auto, low, medium, high) |
| output_format | COMBO | Output format (png, jpeg, webp) |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| code | INT | 0=success, 1=failed, 2=timeout, 999=unknown |
| message | STRING | Status message |
| image | IMAGE | Generated image |

## Links

- [BlueXH](https://bluexh.com/)
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
