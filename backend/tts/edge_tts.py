import asyncio
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
import logging
import edge_tts

from backend.util.constant import audio_dir, novel_fragments_dir
from backend.util.file import read_lines_from_directory


async def _core_generate_speech_async(text: str, output_path: str, voice: str, rate: str):
    """
    异步核心函数，用于生成语音并保存文件。
    """
    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate
        )
        await communicate.save(output_path)
        logging.debug(f"Successfully converted text to speech, path: {output_path}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"An unexpected error occurred during speech generation for path {output_path}, error: {e}")
        raise # Re-raise the exception to be caught by the caller


async def by_edge_tts(text_input: str = None, file_index: int = None, voice: str = "zh-CN-XiaoxiaoNeural", rate: str = "+35%"):
    if text_input is not None and file_index is not None:
        # 单个文本处理
        os.makedirs(audio_dir, exist_ok=True)
        logging.info(f"Generating single audio for index {file_index}, text: {text_input}")
        output_path = os.path.join(audio_dir, f"{file_index}.mp3")
        try:
            await _core_generate_speech_async(text_input, output_path, voice, rate)
            logging.info(f"Finished generating single audio for index {file_index}")
        except Exception as e:
            logging.error(f"Failed to generate single audio for index {file_index}: {e}")
            # Optionally, re-raise or handle as per application requirements
    else:
        # 批量处理
        if os.path.exists(audio_dir):
            shutil.rmtree(audio_dir)
        os.makedirs(audio_dir, exist_ok=True)
        lines, err = read_lines_from_directory(novel_fragments_dir)
        if err:
            logging.error("Failed to read fragments for batch TTS")
            raise Exception("Failed to read fragments")
        if not lines: # Check if lines is empty or None
            logging.warning(f"No novel fragments found in {novel_fragments_dir} for batch TTS")
            return

        logging.info(f"Starting batch TTS for {len(lines)} fragments.")
        
        # Use a wrapper function for ThreadPoolExecutor that calls asyncio.run
        def sync_speech_generation_wrapper(text_line, target_dir, index, speech_voice, speech_rate):
            file_path = os.path.join(target_dir, f"{index}.mp3")
            try:
                asyncio.run(_core_generate_speech_async(text_line, file_path, speech_voice, speech_rate))
            except Exception as e:
                logging.error(f"Error in thread for index {index}: {e}")

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = []
            for i, line in enumerate(lines):
                futures.append(executor.submit(sync_speech_generation_wrapper, line, audio_dir, i, voice, rate))
            for future in futures:
                try:
                    future.result() # 等待所有任务完成并获取结果（或异常）
                except Exception as e:
                    logging.error(f"A thread in batch TTS encountered an error: {e}")
        logging.info("Finished batch TTS processing.")

# The original convert_text_to_speech function is no longer directly called by by_edge_tts's single mode.
# It's effectively replaced by sync_speech_generation_wrapper for the batch mode.
# If convert_text_to_speech was used elsewhere synchronously, it would need similar asyncio.run() treatment.
# For clarity, I'm removing the old convert_text_to_speech as its logic is now split and refined.
# If you need a standalone synchronous version, it would look like sync_speech_generation_wrapper.

# def convert_text_to_speech(line, target_audio_dir, i, voice="zh-CN-XiaoxiaoNeural", rate="+35%"):
#     try:
#         # zh-CN-YunxiNeural  YunjianNeural  rate='25%' YunyangNeural
#         full_path = os.path.join(target_audio_dir, f"{i}.mp3")
#         # This function is now synchronous and uses asyncio.run to call the async core logic
#         asyncio.run(_core_generate_speech_async(line, full_path, voice, rate))
#         logging.debug(f"Successfully converted text to speech for index {i}, path: {full_path}")
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         logging.error(f"An unexpected error occurred for line index {i}, error: {e}")
#         # Consider re-raising or handling more gracefully depending on requirements