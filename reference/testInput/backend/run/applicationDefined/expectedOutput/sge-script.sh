#!/bin/tcsh
#$ -S /bin/tcsh
#$ -cwd
#$  -o output.txt -e error.txt -l netappsali=1G,database=1G,scratch=1G -l arch=lx24-amd64 -r y -j y  -l mem_free=1G -l h_rt=24:00:00 -p 0 -t 1-1
setenv _SALI_JOB_DIR `pwd`
echo "STARTED" > ${_SALI_JOB_DIR}/job-state


set HOME_BIN_DIR="/netapp/sali/peptide/bin/"
set HOME_LIB_DIR="/netapp/sali/peptide/lib/"

set tasks=( seq_batch_1 )
set input=$tasks[$SGE_TASK_ID]

set HOME_RUN_DIR="/netapp/sali/peptide/live/preprocess/nextNewApplicationDefinedTest" 
set HOME_SEQ_BATCH_DIR="$HOME_RUN_DIR/sequenceBatches/$input/"

set NODE_HOME_DIR="/scratch/peptide//$input"
mkdir -p $NODE_HOME_DIR

set PEPTIDE_OUTPUT_FILE_NAME="peptidePipelineOut.txt"
set PARAMETER_FILE_NAME="parameters.txt"

cp $HOME_RUN_DIR/$PARAMETER_FILE_NAME $NODE_HOME_DIR 
cp $HOME_SEQ_BATCH_DIR/inputSequences.fasta $NODE_HOME_DIR

echo -e "\nrun_name\t$input" >>  $NODE_HOME_DIR/$PARAMETER_FILE_NAME     

cd $NODE_HOME_DIR

date
hostname
pwd

setenv PERLLIB $HOME_LIB_DIR



cp $HOME_RUN_DIR/peptideRulesFile $NODE_HOME_DIR
perl $HOME_BIN_DIR/runPeptidePipeline.pl --parameterFileName $PARAMETER_FILE_NAME > & $PEPTIDE_OUTPUT_FILE_NAME

set MODEL_OUTPUT_FILE_NAME="modelPipelineOut.txt"

perl $HOME_BIN_DIR/runModelPipeline.pl --parameterFileName $PARAMETER_FILE_NAME --pipelineClass ApplicationPipeline > & $MODEL_OUTPUT_FILE_NAME

cp -r $NODE_HOME_DIR/* $HOME_SEQ_BATCH_DIR
rm -r $NODE_HOME_DIR/

echo "DONE" > ${_SALI_JOB_DIR}/job-state
