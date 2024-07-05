from enum import Enum
from qa.generative_models.anthropic import get_response as get_response_anthropic
from qa.generative_models.openai import get_response as get_response_openai
from qa.generative_models.google import get_response as get_response_google

class GenerativeModel(Enum):
    CLAUDE_3_HAIKU = 'claude-3-haiku-20240307'
    GPT_3_5_TURBO = 'gpt-3.5-turbo'
    GEMINI_1_5_FLASH = 'gemini-1.5-flash'
    GEMINI_1_5_PRO = 'gemini-1.5-pro'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

GET_RESPONSE = {
    GenerativeModel.CLAUDE_3_HAIKU.value: get_response_anthropic,
    GenerativeModel.GPT_3_5_TURBO.value: get_response_openai,
    GenerativeModel.GEMINI_1_5_FLASH.value: get_response_google,
    GenerativeModel.GEMINI_1_5_PRO.value: get_response_google,
}