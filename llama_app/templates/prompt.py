from enum import Enum
from typing import List

from pydantic import BaseModel


class Role(Enum):
    assistant = "assistant"
    user = "user"


class Inst(BaseModel):
    role: Role
    content: str

    def model_dump(self):
        return {"role": self.role.value, "content": self.content}


B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
BOS, EOS = "<s>", "</s>"

DEFAULT_SYSTEM_PROMPT = f"""You are a helpful, respectful and honest assistant. 
                        Always answer as helpfully as possible, while being safe. Please ensure that your 
                        responses are socially unbiased and positive in nature. If a question does not make any sense, 
                        or is not factually coherent, explain why instead of answering something not correct. 
                        If you don't know the answer to a question, please don't share false information."""


def generate_prompt(messages: List[Inst]):
    message_string = "\n".join([str(Inst(**m).model_dump()) for m in messages])
    return f"""
        {BOS} {B_INST} {B_SYS} {DEFAULT_SYSTEM_PROMPT} {E_SYS} {message_string} {E_INST} {EOS}
    """


if __name__ == "__main__":
    p = generate_prompt(
        [
            {"role": "user", "content": "what is 2+2?"},
            {"role": "assistant", "content": "it's going to be 4"},
        ]
    )
    print(p)


