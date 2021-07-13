import os

for line in open("requirements.txt"):
    os.system(f"pip install {line}")
    os.system('cls')
    print(f"{line} Module installed.")
