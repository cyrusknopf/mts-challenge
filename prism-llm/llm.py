from transformers import AutoModelForCausalLM, AutoTokenizer

# checkpoint = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
checkpoint = "HuggingFaceTB/SmolLM2-360M-Instruct"
device = "cuda"  # cpu, cuda, ipu, xpu, mkldnn, opengl, opencl, ideep, hip, ve, fpga, maia, xla, lazy, vulkan, mps, meta, hpu, mtia, privateuseone

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)

prompt = """### Instructions:
You are a creative text generator tasked with producing a detailed profile synopsis. Given the following information, create an imaginative and comprehensive narrative that includes every provided detail (THIS IS IMPORTANT). The synopsis should serve as contextual input for a system that uses this information to ask you (the reader) to generate a stock portfolio. Therefore, it must clearly capture the key facts while also incorporating additional, sometimes tangential or seemingly irrelevant background details that add depth and character. Avoid simply echoing the input.

### Input:
Name: John Smith
Age: 20
Hates: tech and healthcare businesses
Salary: $10000
Risk Appetite: Low

### Synopsis:
"""

inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)

outputs = model.generate(
    inputs,
    max_length=450,  # Adjust as needed for longer outputs
    do_sample=True,
    top_k=50,
    top_p=0.95,
    temperature=0.9,
    eos_token_id=tokenizer.eos_token_id,
)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
