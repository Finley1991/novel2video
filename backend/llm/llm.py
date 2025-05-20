from backend.llm.openai import query_openai
from backend.llm.sambanova import query_samba_nova
from backend.llm.siliconflow import query_silicon_flow
from backend.util.file import get_config
from backend.util.constant import (
    LLM_MODEL_SILICONFLOW,
    LLM_MODEL_SAMBANOVA,
    LLM_TRANSLATE_SYS_PROMPT,
    LLM_TRANSLATE_MODEL_DEFAULT,
    LLM_TRANSLATE_TEMPERATURE_DEFAULT
)

def query_llm(input_text: str, sys_text: str, model_name: str, temperature: float, max_tokens: int) -> str:
    if model_name == LLM_MODEL_SILICONFLOW:
        return query_silicon_flow(input_text, sys_text, temperature)
    elif model_name == LLM_MODEL_SAMBANOVA:
        return query_samba_nova(input_text, sys_text, model_name, temperature)
    else:
        # For other models, including the default OpenAI ones, pass model_name through
        return query_openai(input_text, sys_text, model_name, temperature)

def llm_translate(input_text: str) -> str:
    # translate_sys = "把输入的中文描述转换成stable diffusion提示词, 中文翻译成英文, 英文逗号分隔" # This line is now replaced by a constant
    return query_openai(input_text, LLM_TRANSLATE_SYS_PROMPT, LLM_TRANSLATE_MODEL_DEFAULT, LLM_TRANSLATE_TEMPERATURE_DEFAULT)


# Example usage:
# result, error = llm_translate("你好")
# if error:
#     print(f"Error: {error}")
# else:
#     print(result)