#!/usr/bin/python
import LaunchOnFarm
from sys import argv

if (len(argv)==2):
    mode = argv[1]
else:
    print "Usage : "+argv[0]+" <input file> <mode=elel,inelel,inelinel>"
    sys.exit(1)
    
if mode=="elel":
    fMode = "ElEl"
elif mode=="inelel":
    fMode = "InelEl"
elif mode=="inelinel":
    fMode = "InelInel"
else:
    sys.exit(2)

FarmDirectory = "/afs/cern.ch/user/l/lforthom/work/LPAIRgen/RECO/"
#FarmDirectory = "RECO/"
#LaunchOnFarm.Jobs_RunHere = 1
LaunchOnFarm.SendCluster_Create(FarmDirectory+fMode, fMode)
NJobs = LaunchOnFarm.SendCluster_LoadInputFiles("step1_"+fMode+"_files.txt", 600)
for i in range(NJobs):
    LaunchOnFarm.SendCluster_Push(["CMSSW", "step2_RECO_cfg.py"])
LaunchOnFarm.SendCluster_Submit()
