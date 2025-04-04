from random import choice
from typing import Any, Dict

from faker import Faker

# from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

flan_instr = "pszemraj/flan-t5-large-instruct-dolly_hhrlhf"
davinci_instr = "zhihz0535/Auto-Instruct-Flan-T5-davinci003-zeroshot"
smollm_135_v2 = "HuggingFaceTB/SmolLM2-135M-Instruct"
smollm_135_v2_unsloth = "unsloth/SmolLM2-135M-Instruct"
gpt_neo = "EleutherAI/gpt-neo-1.3B"
data_to_text = "RUCAIBox/mvp-data-to-text"

MODEL: str = flan_instr
fake = Faker()

hobbies = [
    "painting",
    "hiking",
    "photography",
    "gardening",
    "guitar",
    "cooking",
    "bird watching",
    "rock climbing",
    "knitting",
    "learning languages",
    "woodworking",
]


def prompt(data):
    has_dislikes = len(data["dislikes"]) != 0
    employed = data["employed"]

    base_str = f"""
    You will be given some information about a person. Your sole task is to write a short passage including details about the human. Respond with all included dates

    Input: ```
    Name: {fake.name()}
    Age: {data["age"]}
    their investment start date : {data["start"]}
    their investment end date : {data["end"]}
    hobbies: {choice(hobbies)}
    """

    dislikes_str = (
        f"""
    they avoid : {",".join(data["dislikes"])}
    """
        if has_dislikes
        else ""
    )

    employment_str = (
        f"""
    employed: {data["employed"]}
    Salary: ${data["salary"]} per year```
    """
        if employed
        else ""
    )

    budget_str = f"""
    budget: ${data["budget"]} total

    Output:
    """
    prompt = base_str + dislikes_str + employment_str + budget_str
    return prompt


def init_model(model, device: str = "cuda"):
    tokenizer = AutoTokenizer.from_pretrained(model)
    model = AutoModelForSeq2SeqLM.from_pretrained(model).to(device)
    # model = AutoModelForCausalLM.from_pretrained(model).to(device)
    # tokenizer = MvpTokenizer.from_pretrained(model)
    # model = MvpForConditionalGeneration.from_pretrained(model).to(device)

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
