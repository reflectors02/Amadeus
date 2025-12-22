from patches import apply_all_patches
apply_all_patches()

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import logging
from app import application
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='torch')
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
from tqdm import tqdm
tqdm.disable = True

def run_flask():
    application.run(debug=False, use_reloader=False, port=5000)

if __name__ == "__main__":
    run_flask()






