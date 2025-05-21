import os
from flask import Flask, send_from_directory
from flask_cors import CORS
import logging

from backend.rest_handler.character import get_local_characters, get_new_characters, get_random_appearance, put_characters
from backend.rest_handler.image import generate_images, get_local_images, generate_single_image
from backend.rest_handler.init import get_initial, get_novel_fragments, load_novel, save_combined_fragments, save_novel, \
    save_prompt, load_prompt, get_model_config, save_model_config
from backend.rest_handler.prompt import extract_scene_from_texts, get_prompts_en, save_prompt_en, save_prompt_zh, \
    extract_single_scene_from_text, translate_single_prompt_en
from backend.rest_handler.video import generate_video, get_video
from backend.tts.tts import generate_audio_files, generate_single_audio_file
from backend.util.constant import image_dir, video_dir, audio_dir # audio_dir 会被导入为 "temp/audio"

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s [File: %(filename)s, Line: %(lineno)d]'
)

# novel
@app.route('/api/get/novel/fragments', methods=['GET']) # 获取片段
def api_get_novel_fragments():
    return get_novel_fragments()

@app.route('/api/save/novel/fragments', methods=['POST']) # 切割片段
def api_save_combined_fragments():
    return save_combined_fragments()

# prompts
@app.route('/api/get/novel/prompts', methods=['GET']) # 提取场景
def api_extract_scene_from_texts():
    return extract_scene_from_texts()

@app.route('/api/novel/prompts/en', methods=['GET']) # 获取英文提示词
def api_get_prompts_en():
    return get_prompts_en()

@app.route('/api/novel/prompt/en', methods=['POST']) # 保存英文提示词
def api_save_prompt_en():
    return save_prompt_en()

@app.route('/api/novel/prompt/zh', methods=['POST']) # 保存中文提示词
def api_save_prompt_zh():
    return save_prompt_zh()

@app.route('/api/novel/prompt/zh/single', methods=['POST']) # 单独生成中文prompt
def api_extract_single_scene_from_text_handler():
    return extract_single_scene_from_text()

@app.route('/api/novel/prompt/en/single', methods=['POST']) # 单独翻译英文prompt
def api_translate_single_prompt_en_handler():
    return translate_single_prompt_en()

# image
@app.route('/api/novel/images', methods=['POST']) # 一键生成
def api_generate_image():
    return generate_images()

@app.route('/api/novel/image', methods=['POST']) # 重新生成图片
def api_get_local_image():
    return generate_single_image()

@app.route('/api/novel/images', methods=['GET']) # 获取本地图片
def api_get_local_images():
    return get_local_images()

# 初始化
@app.route('/api/novel/initial', methods=['GET']) # 初始化
def api_get_initial():
    return get_initial()

# tts
@app.route('/api/novel/audio', methods=['POST']) # 生成音频(批量)
def api_generate_audio_files():
    return generate_audio_files()

@app.route('/api/novel/audio/single', methods=['POST']) # 单独生成音频
def api_generate_single_audio_file_handler():
    return generate_single_audio_file()

# character
@app.route('/api/novel/characters', methods=['GET']) # 生成新角色
def api_get_new_characters():
    return get_new_characters()

@app.route('/api/novel/characters/local', methods=['GET']) # 获取本地角色
def api_get_local_characters():
    return get_local_characters()

@app.route('/api/novel/characters', methods=['PUT']) # 保存角色
def api_put_characters():
    return put_characters()

@app.route('/api/novel/characters/random', methods=['GET'])  # 生成随机角色
def api_get_random_appearance():
    return get_random_appearance()

# 获取小说文本
@app.route('/api/novel/load', methods=['GET'])
def api_load_novel():
    return load_novel()

# 保存小说文本
@app.route('/api/novel/save', methods=['POST'])
def api_save_novel():
    return save_novel()

# 获取文生图prompt
@app.route('/api/prompt/load', methods=['GET'])
def api_load_prompt():
    return load_prompt()

# 保存文生图prompt
@app.route('/api/prompt/save', methods=['POST'])
def api_save_prompt():
    return save_prompt()

# 读取视频
@app.route('/api/novel/video', methods=['GET'])
def api_get_video():
   return get_video()

# 生成视频
@app.route('/api/novel/video', methods=['POST'])
def api_generate_video():
   return generate_video()

@app.route('/api/model/config', methods=['GET'])
def api_get_model_config():
   return get_model_config()

@app.route('/api/model/config', methods=['POST'])
def api_save_model_config():
    return save_model_config()

@app.route('/videos/<path:filename>')
def serve_videos(filename):
    return send_from_directory(video_dir, filename)

@app.route('/images/<path:filename>')
def serve_images(filename):
    logging.info(f"Requested image: {filename}")
    file_path = os.path.join(image_dir, filename)
    logging.debug(f"Full path: {file_path}")
    if not os.path.exists(file_path):
        logging.error(f"File not found: {file_path}")
        return "File not found", 404
    return send_from_directory(image_dir, filename)

# 新增以下路由来提供音频文件服务
@app.route('/temp/audio/<path:filename>')
def serve_audio(filename):
    logging.info(f"Requested audio: {filename}")
    # 这里的 audio_dir 是从 constant.py 导入的 "temp/audio"
    file_path = os.path.join(audio_dir, filename) # 这会是 "temp/audio/yourfile.mp3"
    logging.debug(f"Full audio path: {file_path}")
    # os.path.exists 会相对于当前工作目录 (CWD) 检查路径
    # 如果你的 Flask 应用是从项目根目录 (d:\wangyafan\myproject\novel2video) 启动的，
    # CWD 通常就是项目根目录，所以这个检查是正确的。
    if not os.path.exists(file_path):
        logging.error(f"Audio file not found: {file_path}")
        return "Audio file not found", 404
    # send_from_directory 会从相对于 app.root_path 的路径提供文件
    # 如果 audio_dir 是 "temp/audio"，它会从 "app.root_path/temp/audio" 提供文件
    return send_from_directory(audio_dir, filename)

if __name__ == '__main__':
    logging.info(f"Current working directory:{os.getcwd()}")
    app.run(host='localhost', port=8080)
