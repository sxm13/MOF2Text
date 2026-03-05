import os, glob, json, shutil
from mof2text.run import get_prompt
from pathlib import Path
from tqdm import tqdm

os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_THREADING_LAYER'] = 'GNU'
import warnings
warnings.filterwarnings('ignore', message='.*MKL.*')


# examples_folder = "./example"
# cifs = glob.glob(examples_folder+"/*cif")

examples_folder = "./example"
cifs = ["./example/IRMOF-1_pri_p1.cif"]

for cif in cifs[:]:
    data = {}
    prompt = get_prompt(cif)

    data["cif_id"] = Path(cif).stem
    data["mof2text"] = prompt

    with open(os.path.join(examples_folder, Path(cif).stem+".json"), "w") as f:
        json.dump(data,
                  f,
                  ensure_ascii=False,
                  indent=2)
        
    # shutil.rmtree(Path(cif).stem)