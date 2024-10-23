from pathlib import Path

def get_requirements():
    with Path('requirements.txt').open() as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

if __name__ == "__main__":
    print(get_requirements())
