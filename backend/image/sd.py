import json
import logging
import os

import requests
import base64

from backend.util.file import get_config
from backend.util.constant import image_dir, SD_POSITIVE_PROMPT_PREFIX, SD_POSITIVE_PROMPT_SUFFIX, SD_NEGATIVE_PROMPT


async def generate_image(prompt: str, seed: int, width: int, height: int, order):
    try:
        url = get_config()['address3']
        payload = {
            "prompt": SD_POSITIVE_PROMPT_PREFIX + prompt + SD_POSITIVE_PROMPT_SUFFIX,
            "negative_prompt": SD_NEGATIVE_PROMPT,
            "sampler_name": "DPM++ 2M",
            "scheduler": "Karras",
            "scheduler": "Simple",
            # "forge_additional_modules": [
            #     "E:\\sd\\FORGE-V2-\\forge\\models\\VAE\\ae.safetensors",
            #     "E:\\sd\\FORGE-V2-\\forge\\models\\VAE\\clip_l.safetensors",
            #     "E:\\sd\\FORGE-V2-\\forge\\models\\VAE\\t5xxl_fp16.safetensors",
            # ],
            "cfg_scale": 7,
            "steps": 25,
            "width": width,
            "height": height,
            "override_settings": {
                "sd_model_checkpoint":"niji_古风_xl_v1.safetensors",
                "sd_vae": "None",
            },
            "seed":-1,
            "enable_hr": False,
            "hr_scale": 2,
            "denoising_strength": 0.7,
            "hr_upscaler": "R-ESRGAN 4x+",
            "hr_resize_x": 1024,
            "hr_resize_y": 1024,
            "hr_sampler_name": "Euler",
            "hr_second_pass_steps":15,
        }
        # "scheduler": "Simple",
        # "forge_additional_modules": [
        #     "E:\\sd\\FORGE-V2-\\forge\\models\\VAE\\ae.safetensors",
        #     "E:\\sd\\FORGE-V2-\\forge\\models\\VAE\\clip_l.safetensors",
        #     "E:\\sd\\FORGE-V2-\\forge\\models\\VAE\\t5xxl_fp16.safetensors",
        # ],
    except Exception as e:
        logging.error(e)
        return

    try:
        response = requests.post(f"{url}/sdapi/v1/txt2img", json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to make request: {e}")
        return

    try:
        response_data = response.json()
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON response: {e}")
        return

    images = response_data.get("images")
    if not images:
        logging.error("No images found in response")
        return

    try:
        image_data = base64.b64decode(images[0])
    except (IndexError, base64.binascii.Error) as e:
        logging.error(f"Failed to decode image: {e}")
        return

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    output_filename = os.path.join(image_dir, f"{order}.png")

    try:
        with open(output_filename, "wb") as image_file:
            image_file.write(image_data)
    except IOError as e:
        logging.error(f"Failed to write image file: {e}")
        return

    logging.info(f"Image saved to {output_filename}")

# {
#     "prompt": "",
#     "negative_prompt": "",
#     "styles": [
#         "string"
#     ],
#     "seed": -1,
#     "subseed": -1,
#     "subseed_strength": 0,
#     "seed_resize_from_h": -1,
#     "seed_resize_from_w": -1,
#     "sampler_name": "string",
#     "scheduler": "string",
#     "batch_size": 1,
#     "n_iter": 1,
#     "steps": 50,
#     "cfg_scale": 7,
#     "width": 512,
#     "height": 512,
#     "restore_faces": true,
#     "tiling": true,
#     "do_not_save_samples": false,
#     "do_not_save_grid": false,
#     "eta": 0,
#     "denoising_strength": 0,
#     "s_min_uncond": 0,
#     "s_churn": 0,
#     "s_tmax": 0,
#     "s_tmin": 0,
#     "s_noise": 0,
#     "override_settings": {},
#     "override_settings_restore_afterwards": true,
#     "refiner_checkpoint": "string",
#     "refiner_switch_at": 0,
#     "disable_extra_networks": false,
#     "firstpass_image": "string",
#     "comments": {},
#     "enable_hr": false,
#     "firstphase_width": 0,
#     "firstphase_height": 0,
#     "hr_scale": 2,
#     "hr_upscaler": "string",
#     "hr_second_pass_steps": 0,
#     "hr_resize_x": 0,
#     "hr_resize_y": 0,
#     "hr_checkpoint_name": "string",
#     "hr_sampler_name": "string",
#     "hr_scheduler": "string",
#     "hr_prompt": "",
#     "hr_negative_prompt": "",
#     "force_task_id": "string",
#     "sampler_index": "Euler",
#     "script_name": "string",
#     "script_args": [],
#     "send_images": true,
#     "save_images": false,
#     "alwayson_scripts": {},
#     "infotext": "string"
# }