import sys

def expect(expression: bool, failure_message: str):
    if expression: return
    print(f'Error: {failure_message}')
    sys.exit()
