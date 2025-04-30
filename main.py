import warnings
import logging
logging.basicConfig(level=logging.ERROR)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='torch')
from gui import makeWindow

# from tqdm import tqdm
# tqdm.disable = True


makeWindow()