from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

flan_instr = "pszemraj/flan-t5-large-instruct-dolly_hhrlhf"

MODEL : str = flan_instr

prompt = f"""
You will be given some information about a person. Your sole task is to write a short passage including details about the human. Respond with all included dates

Input: ```
Name: {name}
Age: {age}
their investment start date : {start_date}
their investment end date : {end_date}
they avoid : {dislikes.join(", ")}
hobbies: painting
employed: {employed}
budget: ${budget} total
Salary: ${salary} per year```

Output:
"""


def init_model(model, device : str = "cuda"):
    tokenizer = AutoTokenizer.from_pretrained(model)

    model = AutoModelForSeq2SeqLM.from_pretrained(model).to(device)

    return tokenizer, model


def get_response(model, tokenizer device : str = "cuda") -> str:
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)

    outputs = model.generate(
        inputs,
        #min_length=200,
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

    # flan = "google/flan-t5-large"
    # teapot = "teapotai/teapotllm"
    # smoll_360_instr = "HuggingFaceTB/SmolLM-360M-Instruct"
    # smoll_135_instr = "HuggingFaceTB/SmolLM-135M-Instruct"
    # pico = "crumb/pico-gpt-j-6.7m"
    # roberta = "FacebookAI/xlm-roberta-base"
    # lamini = "MBZUAI/LaMini-GPT-774M"
