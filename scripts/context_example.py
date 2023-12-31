# you probably need to make sure that 

instruction = """[INST] <<<.SYS>>>You are a helpful ASSISTANT to CLIENT and you pay close attention to everything that is said in a conversation
before giving a response. You should answer as succinctly as possible, while being safe. There is no need to act conversational, you
can just give a curt and correct response.
<<<./SYS>>>

"""

prompt = instruction + """CLIENT: What are the colors of the rainbow?[/INST]"""

followup = "CLIENT: Now say them in a backwards order."

second_followup = "CLIENT: Now say them in a random order."


def add_prior_context(followup, last_gen):
    
    print(last_gen)

    pattern = re.compile(r'<<<\./SYS>>>(.*?)\[/INST]', re.DOTALL)
    match = pattern.search(last_gen)
    if match:
        # this regex extracts the non-system message prompt that was sent prior.
        last_prompt = match.group(1).strip()
    else:
        raise Exception("error expected llama 2 to include prompt in generated text")
    
    # this matches what was actaully generated by llama after your last prompt
    only_gen = last_gen.split("[/INST]")[1].strip()

    # add the ASSISTANT: prefix to the last answer from llama
    only_gen = "ASSISTANT: " + only_gen
    prompt_with_context = instruction + last_prompt + "\n" + only_gen + "\n" + followup
    return prompt_with_context


import requests
from llama_app.clients.llm import VertexRequest, Prompt
from llama_app.utilities import get_gcp_token
import re

def prompt_with_context(prompt):
    token = get_gcp_token()

    prompt = Prompt(
        prompt=prompt,
        top_k=40,
        max_length=600
        )
    payload = prompt.model_dump()
    print(payload)
    response = requests.post('http://localhost:5000/api/predict', json=payload)
    return response.json()

def print_response(response):
    print(response["predictions"][0][0]["generated_text"])

def run_test():
    response = prompt_with_context(prompt)
    print_response(response)
    # response = prompt_with_context(followup_prompt)
    # print_response(response)
    new_prompt = add_prior_context(followup, response["predictions"][0][0]["generated_text"])
    response = prompt_with_context(new_prompt)
    print_response(response)

if __name__ == "__main__":
    run_test()