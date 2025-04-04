from typing import Any, Dict

from faker import Faker
from transformers import (AutoModelForCausalLM, AutoModelForSeq2SeqLM,
                          AutoTokenizer, MvpForConditionalGeneration,
                          MvpTokenizer)

flan_instr = "pszemraj/flan-t5-large-instruct-dolly_hhrlhf"
davinci_instr = "zhihz0535/Auto-Instruct-Flan-T5-davinci003-zeroshot"
smollm_135_v2 = "HuggingFaceTB/SmolLM2-135M-Instruct"
smollm_135_v2_unsloth = "unsloth/SmolLM2-135M-Instruct"
gpt_neo = "EleutherAI/gpt-neo-1.3B"
data_to_text = "RUCAIBox/mvp-data-to-text"

MODEL: str = data_to_text
fake = Faker()

# prompt = (
#     lambda data: f"""
# You will be given some information about a person. Your sole task is to write a short passage including details about the human. Respond with all included dates
#
# Input: ```
# Name: {fake.name()}
# Age: {data["age"]}
# their investment start date : {data["start"]}
# their investment end date : {data["end"]}
# they avoid : {','.join(data["dislikes"])}
# hobbies: painting
# employed: {data["employed"]}
# budget: ${data["budget"]} total
# Salary: ${data["salary"]} per year```
#
# Output:
# """
# )

prompt = (
    lambda data: f"""
You are given the following information about an individual. Your task is to generate a natural language description that captures all the details provided below in a coherent and engaging narrative.

Input Details:
- Name: {fake.name()}
- Age: {data["age"]}
- Investment Start Date: {data["start"]}
- Investment End Date: {data["end"]}
- Dislikes: {', '.join(data["dislikes"])}
- Hobbies: Painting
- Employment Status: {data["employed"]}
- Total Budget: ${data["budget"]}
- Annual Salary: ${data["salary"]}

Generate a brief yet comprehensive paragraph that summarizes these details.
"""
)


def init_model(model, device: str = "cuda"):
    # tokenizer = AutoTokenizer.from_pretrained(model)
    # model = AutoModelForSeq2SeqLM.from_pretrained(model).to(device)
    # model = AutoModelForCausalLM.from_pretrained(model).to(device)
    tokenizer = MvpTokenizer.from_pretrained(model)
    model = MvpForConditionalGeneration.from_pretrained(model).to(device)

    return tokenizer, model


def get_response(model, tokenizer, data: Dict[str, Any], device: str = "cuda") -> str:
    true_prompt = prompt(data)

    inputs = tokenizer.encode(
        true_prompt,
        return_tensors="pt",
    ).to(device)

    outputs = model.generate(
        inputs,
        # min_length=200,
        min_new_tokens=50,
        max_new_tokens=400,
        do_sample=True,
        top_k=80,
        top_p=0.9,
        temperature=0.3,
        eos_token_id=tokenizer.eos_token_id,
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

    # Model graveyard
    r"""
       _    (^)
      (_\   |_|
       \_\  |_|
       _\_\,/_|
      (`\(_|`\|
     (`\,)  \ \
      \,)   | |      Sai Putravu + Cyrus Knopf
        \__(__|
    """
    # flan = "google/flan-t5-large"
    # teapot = "teapotai/teapotllm"
    # smoll_360_instr = "HuggingFaceTB/SmolLM-360M-Instruct"
    # smoll_135_instr = "HuggingFaceTB/SmolLM-135M-Instruct"
    # pico = "crumb/pico-gpt-j-6.7m"
    # roberta = "FacebookAI/xlm-roberta-base"
    # lamini = "MBZUAI/LaMini-GPT-774M"
