import os
import zipfile
import urllib.request
from tqdm import tqdm

MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip"
MODEL_ZIP_PATH = os.path.join("models", "model_hi.zip")
MODEL_DIR_PATH = os.path.join("models", "vosk-model-small-hi-0.22")
FINAL_MODEL_PATH = os.path.join("models", "vosk-model-small-hi")

def download_file(url, filename):
    class DownloadProgressBar(tqdm):
        def update_to(self, b=1, bsize=1, tsize=None):
            if tsize is not None:
                self.total = tsize
            self.update(b * bsize - self.n)

    with DownloadProgressBar(unit='B', unit_scale=True,
                             miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename=filename, reporthook=t.update_to)

def setup_model():
    if os.path.exists(FINAL_MODEL_PATH):
        print(f"Model already exists at {FINAL_MODEL_PATH}")
        return

    if os.path.exists(MODEL_DIR_PATH):
         print(f"Model directory exists but maybe not renamed. Renaming...")
         try:
            os.rename(MODEL_DIR_PATH, FINAL_MODEL_PATH)
            print("Renamed.")
            return
         except Exception as e:
             print(f"Could not rename: {e}") 

    print("Downloading Vosk Model...")
    if not os.path.exists("models"):
        os.makedirs("models")
    
    download_file(MODEL_URL, MODEL_ZIP_PATH)
    
    print("Extracting...")
    with zipfile.ZipFile(MODEL_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall("models")
    
    # Rename for easier access
    if os.path.exists(MODEL_DIR_PATH):
        os.rename(MODEL_DIR_PATH, FINAL_MODEL_PATH)
    
    # Cleanup
    os.remove(MODEL_ZIP_PATH)
    print("Model setup complete.")

if __name__ == "__main__":
    setup_model()
