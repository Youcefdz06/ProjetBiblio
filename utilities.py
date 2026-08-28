

def ask_yn(prompt):
    x = input(prompt).lower()
    while x not in ("y", "n"):
        x = input("please enter y or n : ").lower()
    return x