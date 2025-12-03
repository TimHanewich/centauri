import rich.prompt

def ask_integer(prompt:str) -> int:
    while True:
        ip:str = rich.prompt.Prompt.ask(prompt)
        try:
            return int(ip)
        except:
            print("Invalid input! Must be an integer.")

def ask_float(prompt:str) -> float:
    while True:
        ip:str = rich.prompt.Prompt.ask(prompt)
        try:
            return float(ip)
        except:
            print("Invalid input! Must be a floating point number.")