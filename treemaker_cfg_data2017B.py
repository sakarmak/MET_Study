import FWCore.ParameterSet.Config as cms
import CondCore.CondDB.CondDB_cfi
from CommonTools.PileupAlgos.customizePuppiTune_cff import UpdatePuppiTuneV14
process = cms.Process("NTuple")

process.load("PhysicsTools.PatAlgos.patSequences_cff")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
setupEgammaPostRecoSeq(process,
                       runVID=False, #saves CPU time by not needlessly re-running VID, if you want the Fall17V2 IDs, set this to True or remove (default is True)
                       era='2017-UL')


from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '106X_dataRun2_v20', '')

#JEC from sqlite file
from CondCore.DBCommon.CondDBSetup_cfi import CondDBSetup
process.jec = cms.ESSource('PoolDBESSource',
    CondDBSetup,
    connect = cms.string('sqlite:Summer19UL17_RunBCDEF_V5_DATA.db'),
    toGet = cms.VPSet(
        cms.PSet(
            record = cms.string('JetCorrectionsRecord'),
            tag    = cms.string('JetCorrectorParametersCollection_Summer19UL17_RunBCDEF_V5_DATA_AK4PFchs'),
            label  = cms.untracked.string('AK4PFchs')
        ),
        cms.PSet(
            record = cms.string('JetCorrectionsRecord'),
            tag    = cms.string('JetCorrectorParametersCollection_Summer19UL17_RunBCDEF_V5_DATA_AK4PFPuppi'),
            label  = cms.untracked.string('AK4PFPuppi')
        ),
    )
)
process.es_prefer_jec = cms.ESPrefer('PoolDBESSource', 'jec')

from RecoJets.JetProducers.ak4PFJets_cfi import ak4PFJets
process.ak4PuppiJets  = ak4PFJets.clone (src = 'puppi', doAreaFastjet = True, jetPtMin = 2.)
from PhysicsTools.PatAlgos.tools.jetTools import addJetCollection                                                                                                                                            
addJetCollection(process,labelName = 'Puppi', jetSource = cms.InputTag('ak4PuppiJets'), algo = 'AK', rParam=0.4, genJetCollection=cms.InputTag('slimmedGenJets'), jetCorrections = ('AK4PFPuppi', ['L1FastJet\
', 'L2Relative', 'L3Absolute'], 'None'),pfCandidates = cms.InputTag('packedPFCandidates'),                                                                                                    
                 pvSource = cms.InputTag('offlineSlimmedPrimaryVertices'),                                                                                                                                   
                 svSource = cms.InputTag('slimmedSecondaryVertices'),                                                                                                                                        
                 muSource =cms.InputTag( 'slimmedMuons'),                                                                                                                                                    
                 elSource = cms.InputTag('slimmedElectrons'),                                                                                                                                                
                 genParticles= cms.InputTag('prunedGenParticles'),                                                                                                                                           
                 getJetMCFlavour= False
)                                                                                                                                                                                                            


process.patJetsPuppi.addGenPartonMatch = cms.bool(False)                                                                                                                                                      
process.patJetsPuppi.addGenJetMatch = cms.bool(False)

UpdatePuppiTuneV14(process, runOnMC=False)

process.load('JetMETCorrections.Configuration.DefaultJEC_cff')
from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection
updateJetCollection(
   process,
   jetSource = cms.InputTag('slimmedJets'),
   labelName = 'UpdatedJEC',
   jetCorrections = ('AK4PFchs', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute']), 'None')  # Update: Safe to always add 'L2L3Residual' as MC contains dummy L2L3Residual corrections (always set to 1)
)
process.updatedPatJetsUpdatedJEC.userData.userFloats.src = []

#Add the files 
readFiles = cms.untracked.vstring()
secFiles = cms.untracked.vstring()
readFiles.extend( [
	"root://cms-xrd-global.cern.ch//store/data/Run2017F/SinglePhoton/MINIAOD/09Aug2019_UL2017-v1/50000/C214F1FC-648B-1645-99C6-57501759D8B9.root",
    ] );

process.source = cms.Source("PoolSource",
    fileNames = readFiles
)

#closes files after code is done running on that file
process.options = cms.untracked.PSet(
	fileMode = cms.untracked.string('NOMERGE')
)

process.load("RecoMET.METFilters.ecalBadCalibFilter_cfi")
baddetEcallist = cms.vuint32(
    [872439604,872422825,872420274,872423218,
     872423215,872416066,872435036,872439336,
     872420273,872436907,872420147,872439731,
     872436657,872420397,872439732,872439339,
     872439603,872422436,872439861,872437051,
     872437052,872420649,872422436,872421950,
     872437185,872422564,872421566,872421695,
     872421955,872421567,872437184,872421951,
     872421694,872437056,872437057,872437313,
     872438182,872438951,872439990,872439864,
     872439609,872437181,872437182,872437053,
     872436794,872436667,872436536,872421541,
     872421413,872421414,872421031,872423083,872421439])
process.ecalBadCalibReducedMINIAODFilter = cms.EDFilter(
    "EcalBadCalibFilter",
    EcalRecHitSource = cms.InputTag("reducedEgamma:reducedEERecHits"),
    ecalMinEt        = cms.double(50.),
    baddetEcal       = baddetEcallist, 
    taggingMode      = cms.bool(True),
    debug            = cms.bool(False)
    )

#input to analyzer
process.content = cms.EDAnalyzer("EventContentAnalyzer")
process.demo = cms.EDAnalyzer('TM',
                              debug_               = cms.untracked.bool(True), 
                              isMC_               = cms.untracked.bool(False),
                              fillgenparticleInfo_ = cms.untracked.bool(False),  #false for data
                              genParticleLabel_    = cms.untracked.InputTag("prunedGenParticles"),
                              genEventLabel_       = cms.untracked.InputTag("generator"),
                              generatorlheLabel_   = cms.untracked.InputTag("source"),
                              filleventInfo_       = cms.untracked.bool(True), 
                              fillpileUpInfo_      = cms.untracked.bool(False),   #false for data
                              pileUpLabel_         = cms.untracked.InputTag("slimmedAddPileupInfo"),
                              filltriggerInfo_     = cms.untracked.bool(True), 
                              hltlabel_            = cms.untracked.string("HLT"),
                              HLTriggerResults_    = cms.untracked.InputTag("TriggerResults","","HLT"),
                              triggerEventTag_     = cms.untracked.InputTag("hltTriggerSummaryAOD","","HLT"),
                              fillvertexInfo_      = cms.untracked.bool(True), 
                              vertexLabel_         = cms.untracked.InputTag("offlineSlimmedPrimaryVertices","",""),
                              fillmuonInfo_        = cms.untracked.bool(True),
                              muonLabel_           = cms.untracked.InputTag("slimmedMuons"),
                              fillPhotInfo_        = cms.untracked.bool(True),  
                              photonLabel_         = cms.untracked.InputTag('slimmedPhotons'),
                              fillelectronInfo_    = cms.untracked.bool(True), 
                              electronLabel_       = cms.untracked.InputTag("slimmedElectrons"),
                              fillrhoInfo_         = cms.untracked.bool(True),  
                              rhoLabel_            = cms.untracked.InputTag("fixedGridRhoFastjetAll"),
                              fillpfmetInfo_       = cms.untracked.bool(True),  
                              pfmetLabel_          = cms.untracked.InputTag("slimmedMETs"),
                              puppimetLabel_       = cms.untracked.InputTag("slimmedMETsPuppi"),  
                              metfilterspatLabel_  = cms.untracked.InputTag("TriggerResults::PAT"),
                              metfiltersrecoLabel_ = cms.untracked.InputTag("TriggerResults::RECO"),
                              ecalBadCalibLabel_   = cms.untracked.InputTag("ecalBadCalibReducedMINIAODFilter"),
                              fillpfjetInfo_       = cms.untracked.bool(True),  
		              pfjetLabel_          = cms.untracked.InputTag("selectedUpdatedPatJetsUpdatedJEC"),
                              filltauInfo_         = cms.untracked.bool(False),
                              tauLabel_            = cms.untracked.InputTag("slimmedTaus"),
                              )

process.TFileService = cms.Service("TFileService",
      fileName = cms.string("histo.root"),
      closeFileFast = cms.untracked.bool(True)
  )


from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
runMetCorAndUncFromMiniAOD(process,
                           isData=True,
                           )

"""from PhysicsTools.PatAlgos.slimming.puppiForMET_cff import makePuppiesFromMiniAOD
makePuppiesFromMiniAOD( process, True )
runMetCorAndUncFromMiniAOD(process,
                           isData=True,
                           metType="Puppi",
                           postfix="Puppi",
                           jetFlavor="AK4PFPuppi",
                           )
process.puppi.useExistingWeights = True"""

#All paths are here
process.p = cms.Path(
    process.egammaPostRecoSeq*
    process.ecalBadCalibReducedMINIAODFilter*
    process.patJetCorrFactorsUpdatedJEC*
    process.updatedPatJetsUpdatedJEC*
    process.selectedUpdatedPatJetsUpdatedJEC*
    process.fullPatMetSequence*
    process.puppiMETSequence*
    process.fullPatMetSequencePuppi*
    process.puppiSequence*
    process.ak4PuppiJets*
    #process.patAlgosToolsTask* 
    process.demo
    )

# reduce verbosity
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(100)

# process number of events
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-100) )

process.schedule=cms.Schedule(process.p)

process.options.numberOfThreads=cms.untracked.uint32(4)
process.options.numberOfStreams=cms.untracked.uint32(0)

#print process.dumpPython()
