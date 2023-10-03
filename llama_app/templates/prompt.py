from enum import Enum
from typing import List

from pydantic import BaseModel


class Role(Enum):
    assistant = "assistant"
    user = "user"
    system = "system"


class Inst(BaseModel):
    role: Role
    content: str

    def model_dump(self):
        return {"role": self.role.value, "content": self.content}


B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
BOS, EOS = "<s>", "</s>"

DEFAULT_SYSTEM_PROMPT = f"""You are a helpful ASSISTANT to USER and you pay close attention to everything 
                            that is said in a conversation before giving a response. You should answer as 
                            succinctly as possible, while being safe. There is no need to act conversational, 
                            you can just give a curt and correct response."""


def generate_prompt(new_prompt, history: List[Inst] = []):
    chat = []
    system = []
    print(history)
    for exchange in [Inst(**m).model_dump() for m in history]:
        if exchange["role"] == "user":
            chat.append(f"{BOS}{B_INST}{exchange['content']}{E_INST}")
        elif exchange["role"] == "assistant":
            chat.append(f"{exchange['content']} {EOS}")
        elif exchange["role"] == "system":
            system.append(
                f"{B_SYS} Please use the following context if it is applicable: {exchange['content']} {E_SYS}"
            )

    return f"""
        {BOS} {B_INST} {B_SYS} {DEFAULT_SYSTEM_PROMPT} {E_SYS} {''.join(system)} Hi There! {E_INST} Hi. How can I help? {EOS} 
            {''.join(chat)} {BOS} {B_INST} {new_prompt} {E_INST}
    """


if __name__ == "__main__":
    import requests

    p = generate_prompt(
        "can you now subtract 2?",
        [
            {"role": "user", "content": "what is 2+2?"},
            {"role": "assistant", "content": "it's going to be 4"},
            {"role": "user", "content": "multiply that by 3"},
            {"role": "assistant", "content": "the answer is 12"},
        ],
    )
    print(p)

    r = requests.post("http://localhost:5000/api/predict", json={"prompt": p})
    print(r.json())
