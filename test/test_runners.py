import unittest
import time
import configobj
import pcssTools
import pcssPeptide
import os
import pcssFeatures
import pcssFeatureHandlers
import pcssErrors
import logging
import sys
import pcssTests
import pcssSvm
import pcssIO
from validate import Validator
#import objgraph


class TestRunner(pcssTests.PcssTest):

    def setupSpecificTest(self):
        self.errorDirName = "ioErrors" #all files for errors are actually in ioErrors
        self.testName = "runner"

    def checkErrorThrown(self, errorType):
        errorInfo = self.runner.getErrorFileInfo()
        self.assertTrue(errorInfo is not None)
        self.assertEquals(errorInfo.errorType, errorType)

    def throwPcssException(self):
        self.pcssConfig["peptide_importer_type"] = "defined"
        self.pcssConfig['fasta_file'] = "testInput/ioErrors/peptideMismatchFasta.txt"
        self.clearErrorFiles()
        self.runner.execute()
        self.assertTrue(os.path.exists(self.runner.pdh.getPcssErrorFile()))

    def throwInternalException(self):
        self.pcssConfig["peptide_importer_type"] = "defined"
        self.pcssConfig['fasta_file'] = "fake"
        self.clearErrorFiles()
        self.runner.execute()
        self.assertTrue(os.path.exists(self.runner.pdh.getInternalErrorFile()))

    def dtest_annotation_pcss_error(self):
        self.runner = pcssTools.AnnotationRunner(self.pcssConfig)
        self.throwPcssException()
        self.checkErrorThrown("pcssError")

    def dtest_svm_application_feature_pcss_error(self):
        self.runner = pcssTools.SvmApplicationFeatureRunner(self.pcssConfig)
        self.throwPcssException()
        self.checkErrorThrown("pcssError")

    def dtest_svm_application_input_pcss_error(self):
        self.pcssConfig["input_annotation_file_name"] = self.getErrorInputFile("missingColumnsFile.txt")
        self.runner = pcssTools.SvmApplicationInputRunner(self.pcssConfig)
        self.clearErrorFiles()
        self.runner.execute()
        self.checkErrorThrown("pcssError")

    def dtest_svm_training_pcss_error(self):
        self.pcssConfig["input_annotation_file_name"] = self.getErrorInputFile("missingColumnsFile.txt")
        self.runner = pcssTools.TrainingBenchmarkRunner(self.pcssConfig)
        self.clearErrorFiles()
        self.runner.execute()
        self.checkErrorThrown("pcssError")
        
    def dtest_annotation_internal_error(self):
        self.runner = pcssTools.AnnotationRunner(self.pcssConfig)
        self.throwInternalException()
        self.checkErrorThrown("internalError")

    def dtest_svm_application_feature_internal_error(self):
        self.runner = pcssTools.SvmApplicationFeatureRunner(self.pcssConfig)
        self.throwInternalException()
        self.checkErrorThrown("internalError")

    def dtest_svm_application_input_internal_error(self):
        self.runner = pcssTools.SvmApplicationInputRunner(self.pcssConfig)
        self.pcssConfig['fasta_file'] = "fake"
        self.clearErrorFiles()
        self.runner.execute()
        self.checkErrorThrown("internalError")

    def dtest_svm_training_input_internal_error(self):
        self.pcssConfig["input_annotation_file_name"] = os.path.join(self.pcssConfig["home_test_directory"], "testInput", "svmTrainingAnnotationInput.txt")
        self.runner = pcssTools.TrainingBenchmarkRunner(self.pcssConfig)
        self.pcssConfig["jackknife_fraction"] = "fake"
        self.clearErrorFiles()
        self.runner.execute()
        self.checkErrorThrown("internalError")        

    def dtest_config_error(self):
        configFile = self.getErrorInputFile("pcssConfigMissingFile.txt")
        configSpecFile = "testConfig/testConfigSpec.txt"
        obj = configobj.ConfigObj(configFile, configspec=configSpecFile)
        with self.assertRaises(pcssErrors.PcssGlobalException) as pge:
            pcssTools.SvmApplicationFeatureRunner(obj)
        self.handleTestException(pge)

    def dtest_svm_application_features_runner(self):
        
        self.executeRunnerTest(self.getLargeFastaFile(), pcssTools.SvmApplicationFeatureRunner, "svmApplication")

    def test_svm_application_features_ump(self):
        self.pcssConfig['fasta_file'] = self.getLargeFastaFile()
        self.pcssConfig['svm_model_file'] = os.path.join(self.pcssConfig['user_pcss_directory'], "data", "benchmark", "userCustomModelFile")
        self.pcssConfig['svm_benchmark_file'] = os.path.join(self.pcssConfig['user_pcss_directory'], "data", "benchmark", "userCustomBenchmarkFile")
        self.runner = pcssTools.SvmApplicationFeatureRunner(self.pcssConfig)
        self.runner.internalConfig['model_table_file'] = self.getFullModelTableFile()
        self.clearErrorFiles()
        self.runner.execute()
        self.assertFalse(os.path.exists(self.runner.pdh.getPcssErrorFile()))
        self.assertFalse(os.path.exists(self.runner.pdh.getInternalErrorFile()))
        self.compareToExpectedOutput(self.runner.pdh.getFullOutputFile(self.runner.internalConfig["annotation_output_file"]),
                                     "svmApplication", False, True)


    def dtest_svm_application_input_runner(self):
        
        self.executeRunnerTest(self.getLargeFastaFile(), pcssTools.SvmApplicationInputRunner, "svmApplication")

    def dtest_annotation_runner(self):
        
        self.executeRunnerTest(self.getLargeFastaFile(), pcssTools.AnnotationRunner, "annotation")

    def dtest_training_annotation_runner(self):
        self.pcssConfig["peptide_importer_type"] = "defined"
        self.executeRunnerTest(self.getLargeDefinedFastaFile(), pcssTools.TrainingAnnotationRunner, "trainingAnnotation")

    def dtest_create_model_runner(self):
        self.runner = pcssTools.CompleteSvmRunner(self.pcssConfig)
        self.executeTrainingRunnerTest(self.runner.pdh.getUserModelFileName(), "userModel")

    def dtest_leave_one_out_runner(self):
        self.runner = pcssTools.LeaveOneOutBenchmarkRunner(self.pcssConfig)
        self.executeTrainingRunnerTest(self.runner.pdh.getLeaveOneOutResultFileName(), "trainingLoo")

    def executeRunnerTest(self, fastaFile, runnerClass, runnerType):
        self.pcssConfig['fasta_file'] = fastaFile

        self.runner = runnerClass(self.pcssConfig)
        self.runner.internalConfig['model_table_file'] = self.getFullModelTableFile()
        self.clearErrorFiles()
        self.runner.execute()
        self.assertFalse(os.path.exists(self.runner.pdh.getPcssErrorFile()))
        self.assertFalse(os.path.exists(self.runner.pdh.getInternalErrorFile()))
        self.compareToExpectedOutput(self.runner.pdh.getFullOutputFile(self.runner.internalConfig["annotation_output_file"]),
                                     runnerType, False, True)

    def executeTrainingRunnerTest(self,  observedOutputFile, runnerType):
        self.pcssConfig["input_annotation_file_name"] = os.path.join(self.pcssConfig["home_test_directory"], "testInput", "svmTrainingAnnotationInput.txt")
        self.clearErrorFiles()
        self.runner.execute()
        self.assertFalse(os.path.exists(self.runner.pdh.getPcssErrorFile()))
        self.assertFalse(os.path.exists(self.runner.pdh.getInternalErrorFile()))
        self.compareToExpectedOutput(observedOutputFile, runnerType, True)

    def dtest_training_svm_runner(self):
        #self.pcssConfig["attribute_file_name"] = os.path.join(self.pcssConfig["pcss_directory"], "data", "context", "trainingFileAttributes.txt")
        self.pcssConfig["input_annotation_file_name"] = os.path.join(self.pcssConfig["home_test_directory"], "testInput", "svmTrainingAnnotationInput.txt")
        self.runner = pcssTools.TrainingBenchmarkRunner(self.pcssConfig)
        self.clearErrorFiles()
        self.runner.internalConfig["make_random_test_set"] = False
        self.runner.execute()
        self.assertFalse(os.path.exists(self.runner.pdh.getPcssErrorFile()))
        self.assertFalse(os.path.exists(self.runner.pdh.getInternalErrorFile()))


if __name__ == '__main__':
    unittest.main()
