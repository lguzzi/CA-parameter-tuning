import subprocess
from io import StringIO


CAThetaCutBarrel = 0.003
CAThetaCutForward = 0.004
dcaCutInnerTriplet = 0.16
dcaCutOuterTriplet = 0.26

#process

output = subprocess.run(['cmsRun','step3_RAW2DIGI_RECO_VALIDATION_DQM.py', 
                f'CAThetaCutBarrel={CAThetaCutBarrel}',
                f'CAThetaCutForward={CAThetaCutForward}',
                f'dcaCutInnerTriplet={dcaCutInnerTriplet}',
                f'dcaCutOuterTriplet={dcaCutOuterTriplet}'],
                capture_output=True,
                text=True)

# ouputFile = open("output.txt", "w")
# ouputFile.write(output.stderr)
# ouputFile.close()

outputLines = StringIO(output.stderr)
totalRec=0
totalAss=0
while line:=outputLines.readline():
    if 'Collection' in line:
        line = outputLines.readline()
        line = outputLines.readline()
        line = outputLines.readline()
        totalRec += int(line.split()[-1])
        line = outputLines.readline()
        totalAss += int(line.split()[-1])

efficiency = totalAss / totalRec
print(efficiency)

