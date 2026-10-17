import sys
from pathlib import Path

# Add project root to sys.path so app modules are resolvable in serverless runtime
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.main import app

# Vercel looks for the ASGI/WSGI app instance
handler = app
