import os
from pathlib import Path

# base_dir = os.path.join(os.getcwd(), "temp")
base_dir = "D:/wangyafan/myproject/novel2video/temp"
image_dir = os.path.join(base_dir, "image")
character_dir = os.path.join(base_dir, "character")
novel_fragments_dir = os.path.join(base_dir, "fragments")
prompts_dir = os.path.join(base_dir, "prompts")
prompts_en_dir = os.path.join(base_dir, "promptsEn")
audio_dir = os.path.join(base_dir, "audio")
video_dir = os.path.join(base_dir, "video")
novel_path = "D:/wangyafan/myproject/novel2video/novel.txt"
prompt_path = "D:/wangyafan/myproject/novel2video/prompt.txt"
config_path = "D:/wangyafan/myproject/novel2video/config.json"

IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 768

# Prompt related constants
FRAGMENTS_PER_LLM_CALL = 30

# Stable Diffusion Prompts
SD_POSITIVE_PROMPT_PREFIX = "ancient chinese, niji style,"
SD_POSITIVE_PROMPT_SUFFIX = "intricate details, masterpiece"
SD_NEGATIVE_PROMPT = "ng_deepnegative_v1_75t,badhandv4 (worst quality:2),(low quality:2),(normal quality:2),lowres,bad anatomy,normal quality,((monochrome)),((grayscale)),(painting by bad-artist-anime:0.9), (painting by bad-artist:0.9), watermark, text, error, blurry, jpeg artifacts, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, artist name,deformed,distorted,disfigured,doll,poorly drawn,bad anatomy,wrong anatomy,bad hand,bad fingers,NSFW"

# LLM related constants
LLM_MODEL_SILICONFLOW = "siliconflow"
LLM_MODEL_SAMBANOVA = "sambanova"
LLM_TRANSLATE_SYS_PROMPT = "把输入的中文描述转换成stable diffusion提示词, 中文翻译成英文, 英文逗号分隔"
LLM_TRANSLATE_MODEL_DEFAULT = "gpt-3.5-turbo"
LLM_TRANSLATE_TEMPERATURE_DEFAULT = 0.01

# Character related prompts
EXTRACT_CHARACTER_SYS = """
	# Task
	从我提供的小说文本中提取出角色名称
	
	# Rule
	1. 提取出所有出现过的角色名字，包含主角和配角
	2. 可以提取人称代词
	3. 不要输出人名、人称代词以外的任何内容
	
	#Output Format:#
	角色1/角色2/角色3/角色4/角色5
"""

APPEARANCE_PROMPT = """
    随机生成动漫角色的外形描述，输出简练，以一组描述词的形式输出，每个描述用逗号隔开
    数量：一个
    包含：衣着，眼睛，发色，发型等等。
    生成男性和女性的概率都为50%
    根据生成的年龄和性别, 输出时在最前方标明1girl/1man/1boy/1lady等等
    示例1: 1boy, white school uniform, brown eyes, short messy black hair.
    示例2: 1girl, short skirt, skinny, blue eyes, blonde hair, twin tails, knee-high socks
    示例3: 1man, Navy suit, Green eyes, short, slicked-back blonde hair
    示例4: 1elderly man, Grey cardigan, Grey eyes, balding with white hair
    使用英文输出，不要输出额外内容
"""
LLM_TRANSLATE_MODEL_DEFAULT = "gpt-3.5-turbo"
LLM_TRANSLATE_TEMPERATURE_DEFAULT = 0.01

import os

# image_dir = os.path.join("temp", "image") # 示例
# video_dir = os.path.join("temp", "video") # 示例

# 添加 audio_dir 定义

# audio_dir = "temp/audio"
print("音频存放位置：", audio_dir)