import subprocess

CAThetaCutBarrel = 0.003
subprocess.run(['cmsRun','step3_RAW2DIGI_RECO_VALIDATION_DQM.py', f'CAThetaCutBarrel={CAThetaCutBarrel}'])