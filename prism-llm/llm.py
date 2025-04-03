import time
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM
from teapotai import TeapotAI

'''
# checkpoint = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
checkpoint = "HuggingFaceTB/SmolLM2-360M-Instruct"
device = "cuda"  # cpu, cuda, ipu, xpu, mkldnn, opengl, opencl, ideep, hip, ve, fpga, maia, xla, lazy, vulkan, mps, meta, hpu, mtia, privateuseone

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)
'''
'''
Input: ```Name: John Smith
Age: 20
Wants to avoid : tech and healthcare businesses
Salary: $10000 per year```

Output:```John Smith is a 20-year-old with a yearly salary of $10,000. When it comes to investing, he prefers to steer clear of tech and healthcare businesses, focusing instead on other opportunities. Outside of finance, John has a keen interest in hiking and often spends his weekends exploring nature trails. He’s also an avid coffee enthusiast, always on the hunt for the perfect brew. In his free time, he enjoys playing chess and occasionally dabbles in painting, though he insists he’s far from an artist.```



'''

prompt = """
You will be given some information about a person. Your sole task is to write a short passage including details about the human and their life. Respond with all included dates

Input: ```
Name: Sandra Patrescu
Age: 40
their investment start date : 01-02-2024
their investment end date : 10-11-2025
they avoid : technology
hobbies: painting
employed: yes
budget: $200 total
Salary: $20,000 per year```

Output:
"""

_= """
You will be given some information about a person. Your sole task is to write a short passage including details about the human. Respond with all included dates

Input: ```
Name: Johnathon Blow
Age: 28
their investment start date : 31-03-2020
their investment end date : 30-12-2024
they avoid : manufacturing
hobbies: painting
employed: yes
budget: $5,000 total
Salary: $80,000 per year```

Output:
"""

def generate_seq(model, device : str = "cuda"):
    tokenizer = AutoTokenizer.from_pretrained(model)

    model = AutoModelForSeq2SeqLM.from_pretrained(model).to(device)


    start = time.time()

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

    end = time.time()

    print(f"Generation took {end - start}.02f")

    print(tokenizer.decode(outputs[0], skip_special_tokens=True))

    return

def generate(model, device : str = "cuda"):
    tokenizer = AutoTokenizer.from_pretrained(model)


    model = AutoModelForCausalLM.from_pretrained(model).to(device)


    start = time.time()

    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)

    outputs = model.generate(
        inputs,
        #max_length=450,  # Adjust as needed for longer outputs
        max_new_tokens=1000,
        do_sample=True,
        top_k=50,
        top_p=0.9,
        temperature=1.1,
        eos_token_id=tokenizer.eos_token_id,
    )

    end = time.time()

    print(f"Generation took {end - start}.02f")

    print(tokenizer.decode(outputs[0], skip_special_tokens=True))

    return


def get_teapot():
    teapot_ai = TeapotAI()

    start = time.time()
    answer = teapot_ai.query(
            query = "Write a profile of this person. You MUST include all details. YOU MUST CREATE TWO NEW DETAILS.",
            context = prompt
    )
    end = time.time()

    print(f"Generation took {end - start}.02f")
    print(answer)


if __name__ == "__main__":
    flan = "google/flan-t5-large"
    flan_instr = "pszemraj/flan-t5-large-instruct-dolly_hhrlhf"
    teapot = "teapotai/teapotllm"
    smoll_360_instr = "HuggingFaceTB/SmolLM-360M-Instruct"
    smoll_135_instr = "HuggingFaceTB/SmolLM-135M-Instruct"
    pico = "crumb/pico-gpt-j-6.7m"
    roberta = "FacebookAI/xlm-roberta-base"
    lamini = "MBZUAI/LaMini-GPT-774M"

    #generate(smoll_360_instr)
    generate_seq(flan_instr)
    

