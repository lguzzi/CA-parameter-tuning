# CA-parameter-tuning
Optimizing geometrical cuts during the pixel seeding step of the CMS High-Level Trigger
## Prerequisites
### Setting up CMSSSW
```
scram p -n cmssw CMSSW_13_2_0
cd cmssw/src
cmsenv
git cms-merge-topic cms-pixel-autotuning:autotuning
scram b -j 4
```
### Creating a Python environment
Install [miniconda](https://docs.conda.io/projects/miniconda/en/latest/), then:
```
conda create -n [env-name] -c conda-forge -y python=3.9 jupyter numpy pandas matplotlib uproot
conda activate [env-name]
```
### Installing The-Optimizer package
The package can be cloned anywhere, but your conda environment must be active during installation.
```
git clone https://github.com/cms-patatrack/The-Optimizer.git
git checkout pixel-autotuning
pip install .
```
### Setting up this repo
Clone the repo:
```
git clone https://github.com/cms-pixel-autotuning/CA-parameter-tuning.git
cd CA-parameter-tuning
```
For Phase-1, there is a script inside the `input` folder that generates the ttbar events used in our optimization. Simply run
```
cd input
. generate_input
```
For other workflows and Phase-2, copy the file(s) produced in step 2 of the workflow to the `input` folder.
## Running Multi-Objective Particle Swarm Optimization (MOPSO)
You can run the whole thing with `python optimize.py` and the following options:
- `-p2`: run the optimization with Phase-2 configuration (Phase-2 input is required)
- `-d`: calculate efficiency and fake rate corresponding to the default cuts that are currently set in CMSSW
- `-e [int]`: number of events to process (<=1000)
- `-i [int]`: number of iterations to run
- `-p [int]`: number of particles to be spawned
- `-c [int]`: continue for a number of iterations (a `checkpoint` folder from a previous run is required)
## Results:
### `checkpoint` folder
- `pareto_front.csv`: the non-dominated solutions across all iterations. Each row corresponds to a particle on the pareto front. The **last** two columns are `1 - efficiency` and `fake rate`, and the rest are the cuts (see [Phase-1 config](https://github.com/cms-pixel-autotuning/CA-parameter-tuning/blob/main/reconstruction.py#L129) or [Phase-2 config](https://github.com/cms-pixel-autotuning/CA-parameter-tuning/blob/main/reconstruction_phase2.py#L132) to know exactly which cut each column corresponds to)
- `default.csv`: onlt one row containing the default cuts and their corresponding `1 - efficiency` and `fake rate`. The columns are the same as in `pareto_front.csv`
- `individual_states.csv`:

