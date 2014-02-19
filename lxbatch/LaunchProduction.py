#!/usr/bin/python

# LaunchProduction.py - Launch an LPAIR events
#  production (step 1 : GEN-SIM-DIGI) once the
#  events' LHE file is provided
# <laurent.forthomme@cern.ch> - Nov 2012

import sys, os
import getopt
from string import replace
from subprocess import call

useCastor = True

def main(argv):
    global fInputs, fOutputs, fLogs

    fNumEvents = 1e5
    fMaxEvents = 100
    
    if len(argv)==3:
        inputFile = argv[1]
        mode = argv[2]
        jobName = mode+'/'
    elif len(argv)==4:
        inputFile = argv[1]
        mode = argv[2]
        jobName = argv[3]+'/'
    else:
        print "Usage : "+argv[0]+" <input file> <mode=elel,inelel,inelinel>"
        sys.exit(1)

    if mode=="elel":
        fMode = "ElEl"
        fLHEfile = "file:/afs/cern.ch/work/l/lforthom/private/LPAIRgen/LHE/events.mumu.el-el.pt15.m0to500.lhe"
    elif mode=="inelel":
        fMode = "InelEl"
        fLHEfile = "file:/afs/cern.ch/work/l/lforthom/private/LPAIRgen/LHE/events.mumu.inel-el.pt15.lhe"
    elif mode=="inelinel":
        fMode = "InelInel"
        fLHEfile = "file:/afs/cern.ch/work/l/lforthom/private/LPAIRgen/LHE/events.mumu.inel-inel.pt15.m0to500.lhe"
    else:
        sys.exit(2)

    if useCastor:
        fOutputDir = "rfio:///castor/cern.ch/user/l/lforthom/LPAIR/"+jobName+"/"
        MakeDirectory(fOutputDir, True)
        fDir = os.getcwd()+"/"+jobName
    else:
        fOutputDir = "file:/afs/cern.ch/work/lforthom/private/LPAIRgen/GEN-SIM-DIGI//"+jobName+"/"
        fDir = fOutputDir
        
    fInputs = fDir+"inputs/"
    fLogs = fDir+"logs/"
    fOutputs = fDir+"outputs/"

    # Create the directory structure
    MakeDirectory(fDir)
    MakeDirectory(fInputs)
    MakeDirectory(fLogs)
    MakeDirectory(fOutputs)
    
    fOutputName = "step1_GEN-SIM-DIGI_"+fMode

    # Create the input and configuration files and send to the cluster
    f = open(inputFile)
    content = f.read()
    for i in range(0,int(fNumEvents/fMaxEvents)):
    #for i in range(1):
        newFile = replace(content, "XXX_ROOTFILE_XXX", fOutputDir+fOutputName+"-"+str(i).zfill(4))
        newFile = replace(newFile, "XXX_I_XXX", str(i).zfill(4))
        newFile = replace(newFile, "XXX_TYPE_XXX", fMode)
        newFile = replace(newFile, "XXX_LHEFILE_XXX", fLHEfile)
        newFile = replace(newFile, "XXX_MAXEVENTS_XXX", str(fMaxEvents))
        newFile = replace(newFile, "XXX_SKIPEVENT_XXX", str(i*fMaxEvents))
        newFile = replace(newFile, "XXX_FIRST_XXX", str(i*fMaxEvents+1))

        of = open(fInputs+"step1_"+str(i).zfill(4)+"_cfg.py", 'w')
        of.write(newFile)
        jf = CreateJobFile(i)
        SendToCluster(jf, i)

def CreateJobFile(i):
    global fInputs
    base = fInputs+"step1_"+str(i).zfill(4)
    f = open(base+".sh", 'w')
    f.write("#!/bin/sh\n")
    f.write("export BASE=`pwd`\n")
    f.write("cd "+os.environ['PWD']+"\n")
    f.write("source /afs/cern.ch/cms/cmsset_default.sh\n")
    f.write("eval `scramv1 runtime -sh`\n")
    f.write("cd $BASE\n")
    f.write("cmsRun "+base+"_cfg.py\n")
    return base+".sh"

def SendToCluster(jobFile, i):
    logBasis = fLogs+str(i).zfill(4)
    logFiles = ['out', 'err']
    for lf in logFiles:
        if os.path.exists(logBasis+'.'+lf):
            try:
                os.remove(logBasis+'.'+lf)
            except:
                print "Exception: ",str(sys.exc_info())
    command = "bsub -q 2nd -R \"tmp>50&&mem>200&&swp>400&&pool>1000\" -o "+logBasis+".out -e "+logBasis+".err `echo sh "+jobFile+"`"
    #print command
    call(command, shell=True)

def MakeDirectory(dir, onCastor=False):
    if onCastor:
        f = dir.split("://")
        if len(f)==2:
            tDir = "/".join(f[1].split("/")[:-2])
            print "[INFO] Accessing CASTOR ("+f[1]+")"
            if call("nsls "+f[1]+" > /dev/null 2>&1", shell=True)!=0:
                call("nsmkdir -p "+f[1], shell=True)
                print "[INFO] "+f[1]+" created !"
    else:
        d = os.path.dirname(dir)
        if not os.path.exists(d):
            os.makedirs(d)

if __name__ == "__main__":
    main(sys.argv)
