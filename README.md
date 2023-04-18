# OpenBioMed
This repository holds OpenBioMed, an open-source toolkit for multi-modal representation learning in AI-driven biomedical research. Our focus is on multi-modal information, e.g. knowledge graphs and biomedical texts for drugs, proteins, and single cells, as well as a wide range of applications, including drug-target interaction prediction, molecular property prediction, cell-type prediction, molecule-text retrieval, molecule-text generation, and drug-response prediction. **Researchers can compose a large number of deep learning models including LLMs like BioMedGPT-1.6B and CellLM to facilitate downstream tasks.** We provide easy-to-use APIs and commands to accelerate life science research.

## News!

- [04/23] 🔥The pre-alpha BioMedGPT model and OpenBioMed are available!

## Features

- **3 different modalities for drugs, proteins, and cell-lines**: molecular structure, knowledge graphs, and biomedical texts. We present a unified and easy-to-use pipeline to load, process, and fuse the multi-modal information.
- **BioMedGPT-1.6B, including other 20 deep learning models**, ranging from CNNs and GNNs to Transformers. **BioMedGPT-1.6B** is a pre-trained multi-modal molecular foundation model with 1.6B parameters that associates 2D molecular graphs with texts. We also present **CellLM**, a single cell foundation model with 50M parameters.  
The checkpoints of BioMedGPT-1.6B and CellLM can be downloaded from [here](https://pan.baidu.com/s/1iAMBkuoZnNAylhopP5OgEg) (password is 7a6b). You can test the performance of BioMedGPT-1.6B on molecule-text retrieval by running scripts/mtr/run.sh, or test the performance of CellLM on cell type classification by running scripts/ctc/train.sh.
- **8 downstream tasks** including AIDD tasks like drug-target interaction prediction and molecule property training, as wel as cross-modal tasks like molecule captioning and text-based molecule generation.  
- **20+ datasets** that are most popular in AI-driven biomedical research. Reproductible benchmarks with abundant model combinations and comprehensive evaluations are provided.
- **3 knowledge graphs** with extensive domain expertise. We present **BMKGv1**, a knowledge graph containing 6,917 drugs, 19,992 proteins, and 2,223,850 relationships with text descriptions. We offer APIs to load and process these graphs and link drugs and proteins based on structural information.

## Installation

To support basic usage of OpenBioMed, run the following command:

```bash
conda create -n OpenBioMed python=3.8
conda activate OpenBioMed
conda install -c conda-forge rdkit
pip install torch

# for torch_geometric, please follow instructions at https://github.com/pyg-team/pytorch_geometric to install the correct version of pyg
pip install torch_cluster-1.6.0-cp38-cp38-linux_x86_64.whl
pip install torch_scatter-2.0.9-cp38-cp38-linux_x86_64.whl
pip install torch_sparse-0.6.14-cp38-cp38-linux_x86_64.whl
pip install torch_spline_conv-1.2.1-cp38-cp38-linux_x86_64.whl
pip install torch-geometric

pip install transformers 
pip install ogb
```

**Note** that additional packages may be required for specific downstream tasks.

## Quick Start

Here, we provide a quick example of training DeepDTA for drug-target interaction prediction on the Davis dataset. For more models, datasets, and tasks, please refer to our [scripts](./open_biomed/scripts) and [documents](./docs).

### Step 1: Data Preparation

Install the Davis dataset [here](https://github.com/hkmztrk/DeepDTA/tree/master/data) and run the following:

```
mkdir datasets
cd datasets
mkdir dti
mv [your_path_of_davis] ./dti/davis
```

### Step 2: Training and Evaluation

Run:

```bash
cd ../open_biomed
bash scripts/dti/train_baseline_regression.sh
```

The results will look like the following (running takes around 40 minutes on an NVIDIA A100 GPU):

```bash
INFO - __main__ - MSE: 0.2198, Pearson: 0.8529, Spearman: 0.7031, CI: 0.8927, r_m^2: 0.6928
```

## Contact Us

As a pre-alpha version release, we are looking forward to user feedback to help us improve our framework. If you have any questions or suggestions, please open an issue or contact [dair@air.tsinghua.edu.cn](mailto:dair@air.tsinghua.edu.cn).


## Cite Us

If you find our open-sourced code & models helpful to your research, please also consider star🌟 and cite📑 this repo. Thank you for your support!
```
@misc{OpenBioMed_code,
  author={Yizhen, Luo and Kai, Yang and Massimo, Hong and Xingyi, Liu and Suyuan, Zhao and Jiahuan Zhang and Yushuai Wu},
  title={Code of OpenBioMed},
  year={2023},
  howpublished = {\url{https://github.com/BioFM/OpenBioMed.git}}
}
```

## Contributing

If you encounter problems using OpenBioMed, feel free to create an issue! 
