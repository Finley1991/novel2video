import json
import logging

from flask import Flask, request, jsonify
import os
import shutil

from backend.util.constant import image_dir, novel_fragments_dir, novel_path, prompts_dir, prompts_en_dir, prompt_path, \
    config_path
from backend.util.file import read_files_from_directory, read_lines_from_directory, save_list_to_files, read_file, \
    read_lines_from_directory_utf8
from backend.util.constant import audio_dir

def handle_error(status_code, message, error):
    response = jsonify({'error': message, 'details': str(error)})
    response.status_code = status_code
    return response

def save_lines_to_files(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            linesWithContent = []
            for line in lines:
                line = line.strip()
                if line:
                    linesWithContent.append(line)
            for i, line in enumerate(linesWithContent):
                file_path = os.path.join(novel_fragments_dir, f"{i}.txt")
                with open(file_path, 'w',encoding='utf-8') as f:
                    f.write(line)
    except Exception as e:
        return e
    return None


def save_combined_fragments():
    fragments = request.json
    if not isinstance(fragments, list):
        return handle_error(400, "Invalid request", "Expected a list of strings")

    try:
        if os.path.exists(novel_fragments_dir):
            shutil.rmtree(novel_fragments_dir, ignore_errors=True)
        os.makedirs(novel_fragments_dir, exist_ok=True)
        error = save_list_to_files(fragments, novel_fragments_dir, 0)
        if error:
            return handle_error(500, "Failed to save", error)
    except Exception as e:
        return handle_error(500, "Failed to process request", e)

    return jsonify({"message": "Fragments saved successfully"}), 200

def get_novel_fragments():
    try:
        if os.path.exists(novel_fragments_dir):
            shutil.rmtree(novel_fragments_dir, ignore_errors=True)
        os.makedirs(novel_fragments_dir, exist_ok=True)
        error = save_lines_to_files(novel_path)
        if error:
            return handle_error(500, "Failed to process file", error)

        lines, error = read_lines_from_directory(novel_fragments_dir)
        if error:
            logging.error(error)
            return handle_error(500, "Failed to read fragments", error)
    except Exception as e:
        logging.error(e)
        return handle_error(500, "Failed to process request", e)

    return jsonify(lines), 200

def get_initial():
    try:
        novels, error = read_lines_from_directory(novel_fragments_dir)
        if error:
            return handle_error(500, "Failed to read fragments", error)

        prompts, error = read_lines_from_directory(prompts_dir)
        if error:
            return handle_error(500, "Failed to read prompts", error)

        prompts_en, error = read_lines_from_directory_utf8(prompts_en_dir)
        if error:
            return handle_error(500, "Failed to read prompts_en", error) # 修正错误信息

        image_files = read_files_from_directory(image_dir)
        images = []
        for file in image_files:
            if not os.path.isdir(os.path.join(image_dir, file)): # 检查完整路径是否为目录
                image_path = os.path.join("/images", file) # 保持相对路径格式
                images.append(image_path)

        audio_file_names = read_files_from_directory(audio_dir) # 读取音频文件名
        audioFiles = []
        if audio_file_names: # 确保 audio_file_names 不是 None
            for file_name in audio_file_names:
                if not os.path.isdir(os.path.join(audio_dir, file_name)): # 检查完整路径是否为目录
                    # 前端期望的路径是 /temp/audio/filename.ext
                    audio_path = os.path.join("/temp/audio", file_name)
                    audioFiles.append(audio_path)
        
        # 为了确保 audioFiles 数组的顺序和数量与 fragments 一致，
        # 并且对于没有对应音频的片段，有一个占位符（例如空字符串或 null）
        # 我们需要根据 fragments 的数量来构建 audioFiles。
        # 假设音频文件名与 fragments 的索引对应 (e.g., 0.mp3, 1.mp3)
        
        num_fragments = len(novels) if novels else 0
        ordered_audio_files = ["" for _ in range(num_fragments)] # 初始化为空字符串

        # 现有逻辑是直接列出 audio_dir 中的所有文件，这可能不按顺序
        # 如果需要严格按片段顺序，需要确保音频文件名能映射到片段索引
        # 例如，如果音频文件名为 "0.mp3", "1.mp3" 等
        
        # 重新整理 audioFiles 以匹配 fragments 的顺序和数量
        # 假设音频文件名是类似 "0.mp3", "1.mp3" 这样的格式
        temp_audio_map = {}
        if audio_file_names:
            for file_name in audio_file_names:
                if not os.path.isdir(os.path.join(audio_dir, file_name)):
                    try:
                        # 尝试从文件名获取索引，例如 "0.mp3" -> 0
                        index_str = os.path.splitext(file_name)[0]
                        index = int(index_str)
                        temp_audio_map[index] = os.path.join("/temp/audio", file_name)
                    except ValueError:
                        logging.warning(f"Could not parse index from audio file name: {file_name}")
                        # 如果文件名不是数字，可以选择忽略或采用其他策略

        for i in range(num_fragments):
            if i in temp_audio_map:
                ordered_audio_files[i] = temp_audio_map[i]
            # else: ordered_audio_files[i] 保持为 ""

        data = {
            "fragments": novels,
            "images": images,
            "prompts": prompts,
            "promptsEn": prompts_en,
            "audioFiles": ordered_audio_files # 添加 audioFiles 数组
        }
    except Exception as e:
        logging.error(f"Error in get_initial: {e}", exc_info=True) # 添加 exc_info=True 获取更详细的堆栈信息
        return handle_error(500, "Failed to process request", str(e))

    return jsonify(data), 200


def load_novel():
    try:
        print("小说文件位置", novel_path)
        content = read_file(novel_path)
        return jsonify({'content': content}), 200
    except FileNotFoundError:
        return jsonify({'content': ''}), 200  
    except Exception as e:
        # import traceback
        # traceback.print_exc()
        return jsonify({'error': str(e)}), 500

def save_novel():
    try:
        data = request.get_json()
        content = data.get('content', '')

        with open(novel_path, 'w', encoding='utf-8') as file:
            file.write(content)

        return jsonify({'message': '保存成功！'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def load_prompt():
    try:
        content = read_file(prompt_path)
        return jsonify({'content': content}), 200
    except FileNotFoundError:
        return jsonify({'content': ''}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def save_prompt():
    try:
        data = request.get_json()
        content = data.get('content', '')

        with open(prompt_path, 'w', encoding='utf-8') as file:
            file.write(content)

        return jsonify({'message': '保存成功！'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_model_config():
    logging.info(f'Config path: {config_path}')
    if not os.path.exists(config_path) or os.path.getsize(config_path) == 0:
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump({'model':'', 'url':'', 'apikey': '', 'address2': '', 'address3': ''}, file)
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logging.info(data['url'])
        return jsonify(data)
    except Exception as e:
        logging.error(f'Error reading addresses: {e}')
        return 'Error reading addresses', 500


def save_model_config():
    try:
        data = request.json
        key = data.get('key')
        value = data.get('value')
        with open(config_path, 'r', encoding='utf-8') as file:
            addresses = json.load(file)
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass  # If it's not a JSON string, keep it as is
        addresses[key] = value
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(addresses, file, ensure_ascii=False, indent=4)
        return 'Address saved successfully', 200
    except Exception as e:
        logging.error(f'Error saving {key}: {e}')
        return f'Error saving {key}', 500