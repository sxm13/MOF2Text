import os, glob, json, shutil
from mof2text.run import get_prompt
from pathlib import Path
from tqdm import tqdm

os.environ['MKL_NUM_THREADS'] = '8'
os.environ['NUMEXPR_NUM_THREADS'] = '8'
os.environ['OMP_NUM_THREADS'] = '8'

os.environ['MKL_THREADING_LAYER'] = 'GNU'
import warnings
warnings.filterwarnings('ignore', message='.*MKL.*')

input_path = "../../dataset/cifs"
jsons = glob.glob("../../dataset/MOFInputs/Txt/*json")
save_path = "./data_prompt"


n_nums = json.load(open("../../dataset/n_atoms/n_atoms_all.json"))
for json_file in tqdm(jsons[:], desc="generating mof2text from CIF..."):

    try:
        data = {}
        cif_id = Path(json_file).stem
        
        cif_path = os.path.join(input_path, cif_id+".cif")
        print(cif_id, n_nums[cif_id])

        if int(n_nums[cif_id])<500:

            prompt = get_prompt(cif_path)

            data["cif_id"] = cif_id
            data["MOF2Text"] = prompt

            with open(os.path.join(save_path,
                                    cif_id+".json"),
                                    "w") as f:
                json.dump(data,
                        f,
                        ensure_ascii=False,
                        indent=2)

            shutil.rmtree(cif_id)
        else:
            print(cif_id, ">500 atoms!")
    except Exception as e:
        print(cif_id, e)
        shutil.rmtree(cif_id)
