from openai import OpenAI, APIError
from loguru import logger
from src.zangief.miner.base_miner import BaseMiner


class OpenAIMiner(BaseMiner):

    def __init__(self):
        super().__init__()
        config = self.get_config()
        self.max_tokens = int(str(config.get_value("max_tokens", 1000)))
        self.temperature = config.get_value("temperature", 0.1)
        self.model = str(config.get_value("model", "gpt-3.5-turbo"))
        openai_key = config.get_value("openai_key", None)
        if openai_key is None:
            raise ValueError("OpenAI key must be specified in the env/config.ini (openai_key = YOUR_KEY_HERE)")
        self.client = OpenAI(api_key=openai_key)
        self.system_prompt = "You are an expert translator who can translate text from a large number of languages. You pay attention to detail providing semantically and grammatically accurate translations quickly and effectively. You will be asked by users to translate text from one language to another. You will not provide any additional context or instructions. Simply return the translated response."

    def generate_translation(self, prompt: str, source_language: str, target_language: str):
        user_prompt = f"Translate the following text from {source_language} to {target_language}: {prompt}"
        system_prompt = self.system_prompt
        completion = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        try:
            translation = completion.choices[0].message.content
        except APIError as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            translation = None

        return translation


if __name__ == "__main__":
    miner = OpenAIMiner()
    OpenAIMiner.start_miner_server(miner)
