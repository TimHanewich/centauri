from rich.console import Console
from rich.prompt import Prompt

console = Console()

# print settings
print()
console.print("[u]Settings[/u]")
console.print("Idle Throttle: [blue]" + str(12) + "%[/blue]")
console.print("Max Throttle: [blue]" + str(13) + "%[/blue]")
print()

confirmed:str = Prompt.ask("Do these settings look good?", choices=["Y","N"], show_choices=True)

print("answer: " + confirmed)