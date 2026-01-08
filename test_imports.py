print("Start Imports...")
try:
    import pandas
    print("Pandas imported")
    import numpy
    print("Numpy imported")
    import gymnasium
    print("Gymnasium imported")
    import torch
    print("Torch imported")
    print(f"Torch version: {torch.__version__}, CUDA: {torch.cuda.is_available()}")
    import stable_baselines3
    print("SB3 imported")
except Exception as e:
    print(f"Error: {e}")
print("End Imports")
