from csv import reader
import subprocess

plot_cmd = ["makeTrackValidationPlots.py"]
for i in range(4):
    dqm_output = "dqm_output" + str(i) + ".root"
    subprocess.run(['cmsRun','full_validation.py', 
                    'dqmOutput=' + dqm_output,
                    'index=' + str(i)])
    if i == 0:
        hist = "default.root"
    else:
        hist = "hist" + str(i) + ".root"
    subprocess.run(['harvestTrackValidationPlots.py', dqm_output, '-o', hist])
    plot_cmd.append(hist)
subprocess.run(plot_cmd)

        
        