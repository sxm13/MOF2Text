<img src="https://raw.githubusercontent.com/sxm13/MOF2Text/main/MOF2text.svg" alt="logo" width="500"/>    

[![Requires Python 3.9](https://img.shields.io/badge/Python-3.9-blue.svg?logo=python&logoColor=white)](https://python.org/downloads) [![MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/sxm13/pypi-dev/blob/main/LICENSE)![Build Status](https://img.shields.io/badge/build-passing-brightgreen) [![Gmail](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:sxmzhaogb@gmail.com) [![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)]() [![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)]() 

#### install
```sh
git clone https://github.com/sxm13/MOF2Text.git
cd MOF2Text
pip install -r requirments.txt

git clone https://github.com/snurr-group/mofid.git
cd mofid
make init
python set_paths.py
pip install .
```

#### usage
```python
from mof2text.run import get_prompt
prompt = get_prompt(cif)
```

*   cif: CIF file 
                           
#### Reference
 
                                            

#### Bugs
If you encounter any problem, please email ```sxmzhaogb@gmail.com```.      