import unittest
import configobj
import pcssTools
import pcssErrors
import pcssIO
import pcssPeptide
import os
import pcssTests

class TestPcssInfrastructure(pcssTests.PcssTest):
    def setupSpecificTest(self):
        self.pcssRunner = pcssTools.PcssRunner(self.pcssConfig)

    def test_copy_file(self):
        sourceDir = "testFileOutput/infrastructure/sourceDir/"
        sourceFile = "testCopy"
        destinationDir = "testFileOutput/infrastructure/destinationDir/"
        self.pcssRunner.pdh.copyFile(sourceDir, sourceFile, destinationDir)
        self.assertTrue(os.path.exists(os.path.join(destinationDir, sourceFile)))
        
        os.remove(os.path.join(destinationDir, sourceFile))
        self.assertRaises(pcssErrors.PcssShutilError, self.pcssRunner.pdh.copyFile, sourceDir + "fake", sourceFile, destinationDir)
        
    def test_move_file(self):

        sourceDir = "testFileOutput/infrastructure/sourceDir/"
        sourceFile = "testMove"
        destinationDir = "testFileOutput/infrastructure/destinationDir/"
        self.pcssRunner.pdh.moveFile(sourceDir, sourceFile, destinationDir)
        self.assertTrue(os.path.exists(os.path.join(destinationDir, sourceFile)))
        
        os.remove(os.path.join(destinationDir, sourceFile))

        self.assertRaises(pcssErrors.PcssShutilError, self.pcssRunner.pdh.moveFile, sourceDir, sourceFile, destinationDir)
        open(os.path.join(sourceDir, sourceFile), 'w').close()

    def test_subprocess_error(self):
        with self.assertRaises(pcssErrors.PcssGlobalException) as pge:
            self.pcssRunner.pdh.unzipFile("fake.gz")
        self.handleTestException(pge)
        self.assertTrue(pge.exception.msg.startswith("Got subprocess error"))
        
    def test_gunzip_error(self):
        with self.assertRaises(pcssErrors.PcssGlobalException) as pge:
            self.pcssRunner.pdh.unzipFile("fake") 
        self.handleTestException(pge)
        #unzipFile raises no .gz in file name before it raises can't find file, so
        #this test relies on that order being maintained
            
        self.assertTrue(pge.exception.msg.startswith("Attempted to unzip"))

    
if __name__ == '__main__':
    unittest.main()

    
