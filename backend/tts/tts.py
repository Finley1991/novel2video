import asyncio # 确保导入 asyncio
from flask import request, jsonify # 确保导入 request 和 jsonify
import logging

from backend.tts.edge_tts import by_edge_tts
from backend.util.constant import audio_dir # 如果需要 audio_dir


def generate_audio_files(): # 这个函数用于批量生成
    try:
        asyncio.run(by_edge_tts()) # 默认调用，处理所有 novel_fragments_dir 中的文件
        return jsonify({"message": "Batch audio generation started successfully"}), 200
    except Exception as e:
        logging.error(f"generate_audio_files error: {e}")
        return jsonify({"error": f"Batch audio generation failed: {str(e)}"}), 500

def generate_single_audio_file():
    req_data = request.get_json()
    print("generate_single_audio_file:line19", req_data)
    if not req_data or 'text' not in req_data or 'index' not in req_data:
        return jsonify({"error": "Invalid request data. 'text' and 'index' are required."}), 400

    text_input = req_data['text']
    file_index = req_data['index']
    # 可以从请求中获取 voice 和 rate，如果希望前端能够指定
    # voice = req_data.get('voice', "zh-CN-XiaoxiaoNeural")
    # rate = req_data.get('rate', "+35%")

    try:
        # asyncio.run(by_edge_tts(text_input=text_input, file_index=file_index, voice=voice, rate=rate))
        # 由于 by_edge_tts 现在是异步的，并且 convert_text_to_speech 内部处理了事件循环，
        # 我们这里也需要 asyncio.run
        asyncio.run(by_edge_tts(text_input=text_input, file_index=file_index))
        file_path = f"{audio_dir}/{file_index}.mp3" # 构造预期的文件路径
        return jsonify({"message": f"Single audio file for index {file_index} generated successfully.", "path": file_path}), 200
    except Exception as e:
        import traceback
        # traceback.print_exc()
        logging.info(f"generate_single_audio_file error: {e}")
        return jsonify({"error": f"Single audio generation failed for index {file_index}: {str(e)}"}), 500