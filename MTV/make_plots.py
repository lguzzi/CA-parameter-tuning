import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-p2', '--phase2', action='store_true')
args = parser.parse_args()

if args.phase2:
    mtv_config = 'mtv_phase2.py'
else:
    mtv_config = 'mtv.py'


plot_cmd = ['makeTrackValidationPlots.py']
for i in range(4):
    dqm_output = 'dqm_output' + str(i) + '.root'
    
    subprocess.run(['cmsRun', mtv_config, 
                    'dqmOutput=' + dqm_output,
                    'index=' + str(i)])
    if i == 0:
        hist = 'default.root'
    else:
        hist = 'hist' + str(i) + '.root'
    subprocess.run(['harvestTrackValidationPlots.py', dqm_output, '-o', hist])
    plot_cmd.append(hist)
subprocess.run(plot_cmd)

        
        