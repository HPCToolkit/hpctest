################################################################################
#                                                                              #
#  slurmExecutor.py                                                            #
#                                                                              #
#  Run jobs immediately or in batch using the SLURM scheduler.                 #
#                                                                              #
#  $HeadURL$                                                                   #
#  $Id$                                                                        #
#                                                                              #
#  --------------------------------------------------------------------------- #
#  Part of HPCToolkit (hpctoolkit.org)                                         #
#                                                                              #
#  Information about sources of support for research and development of        #
#  HPCToolkit is at 'hpctoolkit.org' and in 'README.Acknowledgments'.          #
#  --------------------------------------------------------------------------- #
#                                                                              #
#  Copyright ((c)) 2002-2017, Rice University                                  #
#  All rights reserved.                                                        #
#                                                                              #
#  Redistribution and use in source and binary forms, with or without          #
#  modification, are permitted provided that the following conditions are      #
#  met:                                                                        #
#                                                                              #
#  * Redistributions of source code must retain the above copyright            #
#    notice, this list of conditions and the following disclaimer.             #
#                                                                              #
#  * Redistributions in binary form must reproduce the above copyright         #
#    notice, this list of conditions and the following disclaimer in the       #
#    documentation and/or other materials provided with the distribution.      #
#                                                                              #
#  * Neither the name of Rice University (RICE) nor the names of its           #
#    contributors may be used to endorse or promote products derived from      #
#    this software without specific prior written permission.                  #
#                                                                              #
#  This software is provided by RICE and contributors "as is" and any          #
#  express or implied warranties, including, but not limited to, the           #
#  implied warranties of merchantability and fitness for a particular          #
#  purpose are disclaimed. In no event shall RICE or contributors be           #
#  liable for any direct, indirect, incidental, special, exemplary, or         #
#  consequential damages (including, but not limited to, procurement of        #
#  substitute goods or services; loss of use, data, or profits; or             #
#  business interruption) however caused and on any theory of liability,       #
#  whether in contract, strict liability, or tort (including negligence        #
#  or otherwise) arising in any way out of the use of this software, even      #
#  if advised of the possibility of such damage.                               #
#                                                                              #
################################################################################



from executor import Executor
from common import options


class SlurmExecutor(Executor):
    
    
    def __init__(self):
        
        super(SlurmExecutor, self).__init__()
        # nothing for SlurmExecutor
    

    @classmethod
    def defaultToBackground(cls):
        
        return True

    
    @classmethod
    def isAvailable(cls):
        
        from common import whichDir
        available = whichDir("srun") is not None and whichDir("sbatch") is not None
        return available, "srun and sbatch are missing"


    def run(self, cmd, runPath, env, numRanks, numThreads, outPath, description): # returns nothing, raises
        
        from common import ExecuteFailed
        out, err = _srun(cmd, runPath, env, numRanks, numThreads, outPath, description)
        if err:
            raise ExecuteFailed(out, err)

    
    def submitJob(self, cmd, runPath, env, numRanks, numThreads, outPath, name, description):   # returns jobID, out, err
        
        from common import ExecuteFailed

        jobid, out, err = _sbatch(cmd, runPath, env, numRanks, numThreads, outPath, name, description)
        if err == 0:
            self.runningProcesses.add(jobid)
            self.jobDescriptions[jobid] = description
        
        return jobid, out, err

    
    def isFinished(self, jobID):
        
        from common import notImplemented
        notImplemented("SlurmExecutor.isFinished")
        return True

    
    def pollForFinishedJobs(self):

        from common import notImplemented
        notImplemented("SlurmExecutor.pollForFinishedJobs")
        return set()

    
    def kill(self, process):

        from common import notImplemented
        notImplemented("SlurmExecutor.kill")

    
    def killAll(self):

        from common import notImplemented
        notImplemented("SlurmExecutor.killAll")




def _shell(cmd):
           
    import subprocess
    
    try:
        
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err_out = proc.communicate()
        err = proc.returncode
        if err: out = err_out.strip()
        
    except StandardError as e:
        out = e.strerror
        err = e.errno
    except Exception as e:
        out = str(e)
        err = -1   ## TODO: ??? is there a better property of Exception to use for 'err'?
        
    return out, err


def _srun(cmd, runPath, env, numRanks, numThreads, outPath, description): # returns (out, err)
    
    from os import getcwd
    import textwrap, tempfile
    
    # slurm srun command file template
    ## TODO: this seems to be the same as template in '_sbatch'
    _Slurm_run_template = textwrap.dedent(
        """\
        #!/bin/bash
        #SBATCH --job-name={jobName}
        #SBATCH --account={account}
        #SBATCH --partition={partition}
        #SBATCH --export=NONE
        #SBATCH --exclusive
        #SBATCH --ntasks={numRanks}
        #SBATCH --cpus-per-task={numThreads}
        #SBATCH --mem-per-cpu={memPerThread}
        #SBATCH --time={time}
        #SBATCH --output={outPath}
        #SBATCH --mail-type=NONE
        {cmd}
        """)

    # template params from configuration
    account, partition, time = _paramsFromConfiguration()

    # template params from test
    memPerThread = _paramsFromTest()
    
    # prepare slurm command file
    f = tempfile.NamedTemporaryFile(mode='w+t', bufsize=-1, delete=False,
                                    dir=getcwd(), prefix='sbatch-', suffix=".slurm")
    f.write(_Slurm_run_template.format(
        jobName      = description,
        account      = account,
        partition    = partition,
        numRanks     = numRanks,
        numThreads   = numThreads,
        memPerThread = memPerThread,
        time         = time,
        outPath      = outPath,
        cmd          = cmd,
        ))
    f.close()
    
    # run the command immediately with 'srun'
    out, err = _shell("srun {}".format(f.name))
    
    # extract rc from 'out'
    print "out = '", out, "'"     ## DEBUG
    rc = 0
    
    return out, (err if err else rc)


def _sbatch(cmd, runPath, env, numRanks, numThreads, outPath, name, description): # returns (jobid, out, err)
    
    import textwrap, tempfile
    from os import getcwd
    import common
    from common import verbosemsg
    
    # slurm sbatch command file template
    ## TODO: this seems to be the same as template in '_srun'
    _Slurm_batch_template = textwrap.dedent(
        """\
        #!/bin/bash
        #SBATCH --job-name={jobName}
        #SBATCH --account={account}
        #SBATCH --partition={partition}
        #SBATCH --export=NONE
        #SBATCH --exclusive
        #SBATCH --ntasks={numRanks}
        #SBATCH --cpus-per-task={numThreads}
        #SBATCH --mem-per-cpu={memPerThread}
        #SBATCH --time={time}
        #SBATCH --output={outPath}
        #SBATCH --mail-type=NONE
        {cmd} 
        """)

        ### SBATCH --nodes={nnodes}
        ### SBATCH --ntasks-per-node=1

    # template params from configuration
    account, partition, time = _paramsFromConfiguration()
    
    # template params from test
    memPerThread = _paramsFromTest()
    
    # prepare slurm command file
    f = tempfile.NamedTemporaryFile(mode='w+t', bufsize=-1, delete=False,
                                    dir=getcwd(), prefix='sbatch-', suffix=".slurm")
    f.write(_Slurm_batch_template.format(
        jobName      = name,
        account      = account,
        partition    = partition,
        numRanks     = numRanks,
        numThreads   = numThreads,
        memPerThread = memPerThread,
        time         = time,
        outPath      = outPath,
        cmd          = cmd,
        ))
    f.close()
    
    # submit command file for batch execution with 'sbatch'
    options = "--verbose " if "debug" in common.options else ""
    command = "    sbatch {}{}".format(options, f.name)
    verbosemsg("submitting job {} ...".format(description))
    verbosemsg("    " + command)
    out, err = _shell(command)
    verbosemsg("    " + out)
    verbosemsg("\n")
    
    # handle output from submit command
    if err:
        jobid = rc = None
    else:
        # extract job id from 'out'
        jobid = 17
        # extract rc from 'out'
        rc = 0
    
    return (jobid, out, err if err else rc)


def _envDictToString(envDict):
    
    s = ""
    for key, value in envDict.iteritems():
        s += (key + "=" + value + " ")
    return s


def _paramsFromConfiguration():
    
    import configuration
##  account   =  configuration.get(xxx, "xxx")
##        partition =  configuration.get(xxx, "xxx")
##        time      =  configuration.get(xxx, "xxx")
    account   =  "scott@rice.edu"
    partition =  "common"
    time      =  "0:30:00"
    
    return (account, partition, time)


def _paramsFromTest():
    
    import configuration

    cpusPerTask = 1
    memPerCpu   = "1000m"
    
    return (cpusPerTask, memPerCpu)




# register this executor class by name
Executor.register("Slurm", SlurmExecutor)





