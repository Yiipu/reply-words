#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
/usr/bin/env python3 << 'PYEOF'
import sys, logging
sys.path.insert(0, '.')
from db import run_fade_out
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
faded = run_fade_out()
logging.info(f'Fade-out: {faded} word(s) deactivated')
PYEOF
