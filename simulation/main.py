from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from src.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
