device = "cuda"  # or your preferred device

# Updated prompt with runtime placeholders and additional narrative instructions.


start_date = "01-01-2023"
end_date = "31-11-2024"
age = 30
employment_status = True
budget = 10000
salary = 257774
sector_dislikes = ["Crypto Assets", "Energy and Transportation", "Finance or Crypto Assets"]

prompt = f"""### Instructions:
You are a creative text generator tasked with producing a detailed and natural conversational profile synopsis. Given the following information, craft a rich narrative that integrates every provided detail in a natural and seamless way. Invent a unique name for the person and interweave extra background details—such as hobbies, friends, recent experiences, and personal anecdotes—to create a nuanced character profile. 

Important: Do not mention or hint that this profile is used for generating a US stock portfolio, even though the narrative includes investment details.

### Input:
Name: [Auto-Generated]
Investment Start Date (Buy): {start_date}
Investment End Date (Sell): {end_date}
Age: {age}
Employment Status: {employment_status}
Budget to Invest: ${budget}
Salary: ${salary}
US Stock Sector Dislikes: {','.join(sector_dislikes)}

### Synopsis:
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import time

# Default model; for faster inference consider using Llama2-7B-Chat or MPT-7B-Instruct.
# model_name = "Qwen/Qwen2.5-3B-Instruct"
# model_name = "mistralai/Mixtral-8x7B-Instruct-v0.1"
# model_name = "google/gemma-3-1b-it"
model_name = "HuggingFaceTB/SmolLM2-1.7B-Instruct"


start = time.time()
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)
print(f"Init: {time.time() - start}")
start = time.time()

messages = [
    {"role": "system", "content": "You are an expert at generating stories. You are a helpful assistant, aiming at producing exactly what the user gives you."},
    {"role": "user", "content": prompt}
]

# The placeholders in the prompt (e.g., {start_date}) are expected to be filled in at runtime.
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

print(f"Pre-gen: {time.time() - start}")
start = time.time()
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
# Remove the prompt tokens from the generated output
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]
print(f"Post-gen: {time.time() - start}")
start = time.time()

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(f"Post-decode: {time.time() - start}")
start = time.time()

print(response)

print(f"Pre-gen: {time.time() - start}")
start = time.time()
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
# Remove the prompt tokens from the generated output
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]
print(f"Post-gen: {time.time() - start}")
start = time.time()

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(f"Post-decode: {time.time() - start}")
start = time.time()
