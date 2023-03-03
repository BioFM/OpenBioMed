#!/bin/bash
#SBATCH --job-name open-dair-biomed
#SBATCH --array 0
#SBATCH --gres gpu:a100:1
#SBATCH --time 12:00:00 
#SBATCH --output ../logs/molalbef_zero_shot.log
python tasks/multi_modal_task/mtr.py \
--device cuda:0 \
--dataset PCdes \
--dataset_path ../datasets/mtr/PCdes \
--config_path ./configs/mtr/molalbef.json \
--init_checkpoint ../ckpts/fusion_ckpts/molalbef-graphmvp/checkpoint_299.pth \
--param_key model \
--num_workers 1 \
--mode zero_shot