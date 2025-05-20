import os
import json
import logging
import shutil

from flask import Flask, request, jsonify

from backend.llm.llm import query_llm
from backend.util.constant import character_dir, novel_fragments_dir, EXTRACT_CHARACTER_SYS, APPEARANCE_PROMPT

# extract_character_sys = """
# 	# Task
# 	从我提供的小说文本中提取出角色名称
# 	
# 	# Rule
# 	1. 提取出所有出现过的角色名字，包含主角和配角
# 	2. 可以提取人称代词
# 	3. 不要输出人名、人称代词以外的任何内容
# 	
# 	#Output Format:#
# 	角色1/角色2/角色3/角色4/角色5
# """ # Removed this local variable definition

def get_new_characters():
    try:
        # Remove and recreate the character directory
        if os.path.exists(character_dir):
            shutil.rmtree(character_dir)
        os.makedirs(character_dir)

        # Read lines from the prompts directory
        lines = []
        for file_name in os.listdir(novel_fragments_dir):
            with open(os.path.join(novel_fragments_dir, file_name), 'r', encoding='utf-8') as file:
                lines.extend(file.readlines())

        # Process lines in chunks
        character_map = {}
        for i in range(0, len(lines), 500):
            end = min(i + 500, len(lines))
            prompt = ''.join(lines[i:end])
            print("输入文本：", prompt, "\n", EXTRACT_CHARACTER_SYS)
            response = query_llm(prompt, EXTRACT_CHARACTER_SYS, "gpt-3.5-turbo", 0.01, 8192)
            print("角色：", response)
            for character in response.split('/'):
                character_map[character.strip()] = character.strip()

        # Save characters to a file
        with open(os.path.join(character_dir, 'characters.txt'), 'w') as file:
            json.dump(character_map, file)

        return jsonify(character_map), 200

    except Exception as e:
        logging.error(f"Failed to get new characters: {e}")
        return jsonify({"error": "Failed to get new characters"}), 500


def get_local_characters():
    try:
        if not os.path.exists(character_dir):
            return jsonify({"error":"no local characters"}), 40401
        with open(os.path.join(character_dir, 'characters.txt'), 'r', encoding='utf-8') as file:
            character_map = json.load(file)
        return jsonify(character_map), 200
    except Exception as e:
        logging.error(f"Failed to get local characters: {e}")
        return jsonify({"error": "Failed to get local characters"}), 500

def put_characters():
    try:
        descriptions = request.json
        if not descriptions:
            return jsonify({"error": "Invalid JSON"}), 400

        with open(os.path.join(character_dir, 'characters.txt'), 'r', encoding='utf-8') as file:
            character_map = json.load(file)

        character_map.update(descriptions)
        # Save descriptions to a file
        with open(os.path.join(character_dir, 'characters.txt'), 'w', encoding='utf-8') as file:
            json.dump(character_map, file, ensure_ascii=False, indent=4)

        return jsonify({"message": "Descriptions updated successfully"}), 200

    except Exception as e:
        logging.error(f"Failed to put characters: {e}")
        return jsonify({"error": "Failed to put characters"}), 500

# appearance_prompt = """
#     随机生成动漫角色的外形描述，输出简练，以一组描述词的形式输出，每个描述用逗号隔开
#     数量：一个
#     包含：衣着，眼睛，发色，发型等等。
#     生成男性和女性的概率都为50%
#     根据生成的年龄和性别, 输出时在最前方标明1girl/1man/1boy/1lady等等
#     示例1: 1boy, white school uniform, brown eyes, short messy black hair.
#     示例2: 1girl, short skirt, skinny, blue eyes, blonde hair, twin tails, knee-high socks
#     示例3: 1man, Navy suit, Green eyes, short, slicked-back blonde hair
#     示例4: 1elderly man, Grey cardigan, Grey eyes, balding with white hair
#     使用英文输出，不要输出额外内容
# """ # Removed this local variable definition

def get_random_appearance():
    try:
        prompt = APPEARANCE_PROMPT
        appearance = query_llm(prompt, "", "doubao", 1, 100)
        return jsonify(appearance), 200
    except Exception as e:
        logging.error(f"Failed to get random appearance: {e}")
        return jsonify({"error": "Failed to get random appearance"}), 400