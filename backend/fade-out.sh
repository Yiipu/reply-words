#!/bin/bash
cd /home/opal/workspace/reply-words/backend
/usr/bin/python3 << 'PYEOF'
import sys, os, logging
sys.path.insert(0, os.getcwd())
from db import run_fade_out
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
faded = run_fade_out()
logging.info(f'Fade-out: {faded} word(s) removed')
PYEOF
