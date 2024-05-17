from re import sub

def snake_case(s: str) -> str:
    return s.lower().replace(":", "|").replace(" ", "_")