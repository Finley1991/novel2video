import json
from flask import Flask, request, jsonify
import os
import shutil
import re
import concurrent.futures
import logging
from backend.llm.llm import llm_translate, query_llm
from backend.util.constant import character_dir, novel_fragments_dir, prompts_dir, prompts_en_dir, prompt_path, FRAGMENTS_PER_LLM_CALL
from backend.util.file import read_lines_from_directory, save_list_to_files, read_file, save_text_to_file

# fragmentsLen = 30 # Removed this line

# Function to generate input prompts
def generate_input_prompts(lines, step):
    prompts = []
    for i in range(0, len(lines), step):
        end = min(i + step, len(lines))
        prompt = "\n".join(f"{j}. {lines[j]}" for j in range(i, end))
        logging.info(f"prompt is {prompt}")
        prompts.append(prompt)
    return prompts

# Function to translate prompts
def translate_prompts(lines):
    def translate_line(line):
        res = llm_translate(line)
        return res

    with concurrent.futures.ThreadPoolExecutor() as executor:
        translated_lines = list(executor.map(translate_line, lines))
    return translated_lines

def extract_scene_from_texts():
    try:
        lines, err = read_lines_from_directory(novel_fragments_dir)
        if err:
            return jsonify({"error": "Failed to read fragments"}), 500
    except Exception as e:
        return jsonify({"error": "Failed to read fragments"}), 500

    try:
        if os.path.exists(prompts_dir):
            shutil.rmtree(prompts_dir)
        os.makedirs(prompts_dir)
    except Exception as e:
        return jsonify({"error": "Failed to manage directory"}), 500

    prompts_mid = generate_input_prompts(lines, FRAGMENTS_PER_LLM_CALL)
    offset = 0
    sys = read_file(prompt_path)
    for p in prompts_mid:
        res = query_llm(p, sys, "x", 1, 8192)
        logging.info(res)
        lines = res.split("\n")
        re_pattern = re.compile(r'^\d+\.\s*')
        t2i_prompts = [re_pattern.sub('', line) for line in lines if line.strip()]
        offset += len(t2i_prompts)
        try:
            logging.info(f"len is {len(t2i_prompts)}")
            # print("prompts_dir ", prompts_dir)
            save_list_to_files(t2i_prompts, prompts_dir, offset - len(t2i_prompts))
        except Exception as e:
            return jsonify({"error": "save list to file failed"}), 500

    
    lines, err = read_lines_from_directory(prompts_dir)
    if err:
        return jsonify({"error": "Failed to read fragments"}), 500
    
       

    logging.info("extract prompts from novel fragments finished")
    return jsonify(lines), 200

def get_prompts_en():
    try:
        if os.path.exists(prompts_en_dir):
            shutil.rmtree(prompts_en_dir)
        os.makedirs(prompts_en_dir)
    except Exception as e:
        return jsonify({"error": "Failed to manage directory"}), 500

    
    lines, err = read_lines_from_directory(prompts_dir)
    if err:
        return jsonify({"error": "Failed to read fragments"}), 500

    try:
        character_map = {}
        p = os.path.join(character_dir, 'characters.txt')
        if os.path.exists(p):
            with open(p, 'r', encoding='utf8') as file:
                    character_map = json.load(file)

        for i, line in enumerate(lines):
            for key, value in character_map.items():
                if key in line:
                    lines[i] = lines[i].replace(key, value)
                    break
        # print("character map is ", character_map)
    except Exception as e:
        logging.error(f"translate prompts failed, err {e}")
        return jsonify({"error": "translate failed"}), 500

    try:
        lines = translate_prompts(lines)
    except Exception as e:
        logging.error(f"translate prompts failed, err {e}")
        return jsonify({"error": "translate failed"}), 500

    try:
        save_list_to_files(lines, prompts_en_dir, 0)
    except Exception as e:
        return jsonify({"error": "Failed to save promptsEn"}), 500

    logging.info("translate prompts to English finished")
    return jsonify(lines), 200

def save_prompt_en():
    req = request.get_json()
    if not req or 'index' not in req or 'content' not in req:
        return jsonify({"error": "parse request body failed"}), 400

    file_path = os.path.join(prompts_en_dir, f"{req['index']}.txt")
    try:
        os.makedirs(prompts_en_dir, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(req['content'])
    except Exception as e:
        return jsonify({"error": "Failed to write file"}), 500

    return jsonify({"message": "Attachment saved successfully"}), 200

def save_prompt_zh():
    req = request.get_json()
    if not req or 'index' not in req or 'content' not in req:
        return jsonify({"error": "parse request body failed"}), 400

    file_path = os.path.join(prompts_dir, f"{req['index']}.txt")
    try:
        os.makedirs(prompts_dir, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(req['content'])
    except Exception as e:
        return jsonify({"error": "Failed to write file"}), 500

    return jsonify({"message": "Attachment saved successfully"}), 200


def extract_single_scene_from_text():
    req_data = request.get_json()
    if not req_data or 'text' not in req_data or 'index' not in req_data:
        return jsonify({"error": "Invalid request data. 'text' and 'index' are required."}), 400

    input_text = req_data['text']
    index = req_data['index']

    try:
        sys_prompt_content = read_file(prompt_path)
        if not sys_prompt_content:
            return jsonify({"error": "Failed to read system prompt file"}), 500

        # 构建单行输入给LLM，模仿 generate_input_prompts 的单项输入
        # 这里我们假设LLM可以直接处理单行文本进行场景提取
        # 如果需要特定格式，例如 "0. text_content"，则需要相应调整
        # formatted_input_text = f"{index}. {input_text}" # 根据LLM的需要调整
        
        # 使用 query_llm 生成中文 prompt
        # 注意：这里的 "x" model_name 和 temperature, max_tokens 可能需要根据实际配置调整
        # 这里的 model_name="x" 是基于 extract_scene_from_texts 中的用法，可能需要一个更合适的模型名称
        chinese_prompt = query_llm(input_text, sys_prompt_content, "x", 1, 8192) 
        
        # 移除可能存在的序号前缀，例如 "0. "
        re_pattern = re.compile(r'^\d+\.\s*')
        cleaned_prompt = re_pattern.sub('', chinese_prompt).strip()

        if not cleaned_prompt:
             cleaned_prompt = input_text # 如果提取失败，使用原始输入

        # 保存生成的中文 prompt
        file_path = os.path.join(prompts_dir, f"{index}.txt")
        save_text_to_file(cleaned_prompt, file_path)
        
        logging.info(f"Successfully extracted single Chinese prompt for index {index}: {cleaned_prompt}")
        return jsonify({"prompt": cleaned_prompt, "index": index}), 200

    except Exception as e:
        logging.error(f"Failed to extract single scene: {e}")
        return jsonify({"error": f"Failed to extract single scene: {str(e)}"}), 500

def translate_single_prompt_en():
    req_data = request.get_json()
    if not req_data or 'text' not in req_data or 'index' not in req_data:
        return jsonify({"error": "Invalid request data. 'text' and 'index' are required."}), 400

    chinese_prompt = req_data['text']
    index = req_data['index']

    try:
        character_map = {}
        p = os.path.join(character_dir, 'characters.txt')
        if os.path.exists(p):
            with open(p, 'r', encoding='utf8') as file:
                    character_map = json.load(file)
        
    except Exception as e:
        logging.error(f"translate prompts failed, err {e}")
        return jsonify({"error": "translate failed"}), 500

    try:
        # 翻译中文 prompt 到英文
        for key, value in character_map.items():
            if key in chinese_prompt:
                chinese_prompt = chinese_prompt.replace(key, value)
                # 只替换第一个匹配项，避免重复替换
                break
        english_prompt = llm_translate(chinese_prompt)


        # 保存翻译后的英文 prompt
        file_path = os.path.join(prompts_en_dir, f"{index}.txt")
        save_text_to_file(english_prompt, file_path)

        logging.info(f"Successfully translated single prompt to English for index {index}: {english_prompt}")
        return jsonify({"prompt_en": english_prompt, "index": index}), 200

    except Exception as e:
        logging.error(f"Failed to translate single prompt to English: {e}")
        return jsonify({"error": f"Failed to translate single prompt to English: {str(e)}"}), 500