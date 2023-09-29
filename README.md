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
Install [miniconda](https://docs.conda.io/projects/miniconda/en/latest/), then
```
conda create -n [env-name] -c conda-forge -y python=3.9 jupyter numpy pandas matplotlib uproot
```
