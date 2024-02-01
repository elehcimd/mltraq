from mltraq import options

print("Before", options.get("reproducibility.random_seed"))
with options.ctx({"reproducibility.random_seed": 444}):
    print("Inside", options.get("reproducibility.random_seed"))
print("After", options.get("reproducibility.random_seed"))
