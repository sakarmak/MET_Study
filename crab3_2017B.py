from CRABClient.UserUtilities import config #, getUsernameFromSiteDB
config = config()

config.General.requestName = 'SinglePhotonB'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.allowUndistributedCMSSW = True
config.JobType.maxJobRuntimeMin = 300
config.JobType.numCores = 4
config.JobType.maxMemoryMB = 9000
config.JobType.psetName = '/afs/cern.ch/work/s/sakarmak/private/UL_CMSSW_10_6_2/CMSSW_10_6_2/src/GammaJets/TM/test/treemaker_cfg_data2017B.py'
config.JobType.pluginName = 'Analysis'
config.JobType.outputFiles = ['histo.root']
config.JobType.inputFiles = ['Summer19UL17_RunBCDEF_V5_DATA.db']

config.Data.inputDataset = '/SinglePhoton/Run2017B-09Aug2019_UL2017-v1/MINIAOD'
config.Data.unitsPerJob = 1
config.Data.splitting = 'FileBased'
config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions17/13TeV/Legacy_2017/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt'
config.Data.outLFNDirBase = '/store/user/sakarmak/'

config.Site.storageSite = 'T2_IN_TIFR'

