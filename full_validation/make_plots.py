from csv import reader
import subprocess

plot_cmd = ["makeTrackValidationPlots.py", "default.root"]
with open("selected_params.csv", "r") as f:
    csv_reader = reader(f)
    for i, row in enumerate(csv_reader):
        dqm_output = "dqm_output" + str(i) + ".root"
        subprocess.run(['cmsRun','full_validation.py', 
                        'CAThetaCutBarrel=' + row[0], 
                        'CAThetaCutForward=' + row[1], 
                        'dcaCutInnerTriplet=' + row[2], 
                        'dcaCutOuterTriplet=' + row[3], 
                        'dqmOutput=' + dqm_output])
        hist = "hist" + str(i) + ".root"
        subprocess.run(['harvestTrackValidationPlots.py', dqm_output, '-o', hist])
        plot_cmd.append(hist)
        
subprocess.run(plot_cmd)

        
        