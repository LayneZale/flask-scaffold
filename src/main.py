import os
import sys

from . import create_app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'common'))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
sys.path.insert(0, os.path.join(BASE_DIR, 'cabits-libs'))

app = create_app()
if __name__ == '__main__':
    app.run()
