# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: step3 -s RAW2DIGI:RawToDigi_pixelOnly,RECO:reconstruction_pixelTrackingOnly,VALIDATION:@pixelTrackingOnlyValidation,DQM:@pixelTrackingOnlyDQM --conditions 131X_mcRun4_realistic_v2 --datatier DQMIO -n 10 --eventcontent DQM --geometry Extended2026D98 --era Phase2C17I13M9 --procModifiers pixelNtupletFit,gpu --filein file:step2_phase2.root --fileout file:step3.root --no_exec
import FWCore.ParameterSet.Config as cms
import numpy as np

from Configuration.Eras.Era_Phase2C17I13M9_cff import Phase2C17I13M9
from Configuration.ProcessModifiers.pixelNtupletFit_cff import pixelNtupletFit
from Configuration.ProcessModifiers.gpu_cff import gpu

process = cms.Process('RECO',Phase2C17I13M9,pixelNtupletFit,gpu)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.Geometry.GeometryExtended2026D98Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.Validation_cff')
process.load('DQMServices.Core.DQMStoreNonLegacy_cff')
process.load('DQMOffline.Configuration.DQMOfflineMC_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

# import VarParsing
from FWCore.ParameterSet.VarParsing import VarParsing

# VarParsing instance
options = VarParsing('analysis')

options.register ('parametersFile',
              "../checkpoint/selected_params.csv",
              VarParsing.multiplicity.singleton,
              VarParsing.varType.string,
              "File containing selected parameters")

options.register ('index',
                0,
                VarParsing.multiplicity.singleton,
                VarParsing.varType.int,
                "index")

options.register ('dqmOutput',
              "dqm_ouput.root",
              VarParsing.multiplicity.singleton,
              VarParsing.varType.string,
              "Output file name")

options.parseArguments()

params = np.genfromtxt(options.parametersFile, delimiter=",", dtype=float)[int(options.index)]

process.pixelTracksCUDA.CAThetaCutBarrel = cms.double(params[0])
process.pixelTracksCUDA.CAThetaCutForward = cms.double(params[1])
process.pixelTracksCUDA.dcaCutInnerTriplet = cms.double(params[2])
process.pixelTracksCUDA.dcaCutOuterTriplet = cms.double(params[3])
process.pixelTracksCUDA.hardCurvCut = cms.double(params[4])
process.pixelTracksCUDA.z0Cut = cms.double(params[5])
process.pixelTracksCUDA.phiCuts = cms.vint32(
    int(params[6]), int(params[7]), int(params[8]), int(params[9]), int(params[10]),
    int(params[11]), int(params[12]), int(params[13]), int(params[14]), int(params[15]),
    int(params[16]), int(params[17]), int(params[18]), int(params[19]), int(params[20]),
    int(params[21]), int(params[22]), int(params[23]), int(params[24]), int(params[25]),
    int(params[26]), int(params[27]), int(params[28]), int(params[29]), int(params[30]),
    int(params[31]), int(params[32]), int(params[33]), int(params[34]), int(params[35]),
    int(params[36]), int(params[37]), int(params[38]), int(params[39]), int(params[40]),
    int(params[41]), int(params[42]), int(params[43]), int(params[44]), int(params[45]),
    int(params[46]), int(params[47]), int(params[48]), int(params[49]), int(params[50]),
    int(params[51]), int(params[52]), int(params[53]), int(params[54]), int(params[55]),
    int(params[56]), int(params[57]), int(params[58]), int(params[59]), int(params[60])
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(100),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring('file:../input/step2_phase2.root'),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    FailPath = cms.untracked.vstring(),
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    SkipEvent = cms.untracked.vstring(),
    accelerators = cms.untracked.vstring('*'),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(False),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    holdsReferencesToDeleteEarly = cms.untracked.VPSet(),
    makeTriggerResults = cms.obsolete.untracked.bool,
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('step3 nevts:100'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.DQMoutput = cms.OutputModule("DQMRootOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('DQMIO'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string("file:" + options.dqmOutput),
    outputCommands = process.DQMEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

# Additional output definition

# Other statements
process.mix.playback = True
process.mix.digitizers = cms.PSet()
for a in process.aliases: delattr(process, a)
process.RandomNumberGeneratorService.restoreStateLabel=cms.untracked.string("randomEngineStateProducer")
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic_T21', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi_pixelOnly)
process.reconstruction_step = cms.Path(process.reconstruction_pixelTrackingOnly)
process.prevalidation_step = cms.Path(process.globalPrevalidationPixelTrackingOnly)
process.validation_step = cms.EndPath(process.globalValidationPixelTrackingOnly)
process.dqmoffline_step = cms.EndPath(process.DQMOfflinePixelTracking)
process.dqmofflineOnPAT_step = cms.EndPath(process.PostDQMOffline)
process.DQMoutput_step = cms.EndPath(process.DQMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.raw2digi_step,process.reconstruction_step,process.prevalidation_step,process.validation_step,process.dqmoffline_step,process.dqmofflineOnPAT_step,process.DQMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.
process.options.numberOfThreads = 10
process.options.numberOfStreams = 0

# Automatic addition of the customisation function from SimGeneral.MixingModule.fullMixCustomize_cff
from SimGeneral.MixingModule.fullMixCustomize_cff import setCrossingFrameOn 

#call to customisation function setCrossingFrameOn imported from SimGeneral.MixingModule.fullMixCustomize_cff
process = setCrossingFrameOn(process)

# Automatic addition of the customisation function from RecoTracker.Configuration.customizePixelTracksForTriplets
from RecoTracker.Configuration.customizePixelTracksForTriplets import customizePixelTracksForTriplets 

#call to customisation function customizePixelTracksForTriplets imported from RecoTracker.Configuration.customizePixelTracksForTriplets
process = customizePixelTracksForTriplets(process)

# Customisation from command line

#Have logErrorHarvester wait for the same EDProducers to finish as those providing data for the OutputModule
from FWCore.Modules.logErrorHarvester_cff import customiseLogErrorHarvesterUsingOutputCommands
process = customiseLogErrorHarvesterUsingOutputCommands(process)

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion
