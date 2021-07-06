#!/bin/bash
########## Begin SLURM header ##########
#SBATCH --job-name=wtfree5pr
# Request number of nodes and CPU cores per node for job
#SBATCH --partition=gpu-single
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --cpus-per-gpu=40
#SBATCH --gres=gpu:1
#SBATCH --mem=64g
#SBATCH --time=12:00:00
#SBATCH -o ./slurm_%j_wtfree5ma.log
#SBATCH -e ./slurm_%j_wtfree5ma.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=wi192@uni-heidelberg.de
########### End SLURM header ##########
module load devel/cuda/10.1
module load compiler/gnu/5.2
module load lib/cudnn/7.6.5-cuda-10.1
cd $HOME/ariel/dlc-quick
export DLClight=True
eval "$($HOME/miniconda/bin/conda shell.bash hook)"
conda init bash
conda activate quick-dlc
export OMP_NUM_THREADS=10
export PYTHONPATH=$PWD:$PYTHONPATH
echo "LIST OF FILES"
python training.py --task wtfree5ma-agkuner-2021-06-25 --working-dir projects --video projects/wtfree5ma-agkuner-2021-06-25/videos  --snapshot snapshot-3400 --train n > 'wtfree5ma.out' 2>&1
