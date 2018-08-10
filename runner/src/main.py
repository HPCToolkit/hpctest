################################################################################
#                                                                              #
#  main.py                                                                     #
#  main program, converts Unix-style command line to HPCTest method calls      #
#                                                                              #
#  $HeadURL$                                                                   #
#  $Id$                                                                        #
#                                                                              #
#  --------------------------------------------------------------------------- #
#  Part of HPCToolkit (hpctoolkit.org)                                         #
#                                                                              #
#  Information about sources of support for research and development of        #
#  HPCToolkit is at "hpctoolkit.org" and in "README.Acknowledgments".          #
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


#### TEMPORARY: ALL CODE INVOLVING 'numrepeats' IS STUBBED OUT FOR NOW


from hpctest import HPCTest

global tester
tester = HPCTest()      # must come early b/c initializes paths in common.*




def main():
        
    args = parseCommandLine()    
    return execute(args)


def parseCommandLine():
    # see https://docs.python.org/2/howto/argparse.html
    
    import argparse
    from os.path import join
    import common
    global tester
    
    # default values
    workpath = join(common.homepath, "work")
    
    # parsers
    parser = argparse.ArgumentParser(prog="hpctest")
    subparsers = parser.add_subparsers(dest="subcommand")

    # info ...

    # settings ...
    
    
    # -------------------------------------------------------------------------------------------------------
    # hpctest run [tspec | --tests tspec] [--configs cspec] [--workspace workspace] <options>
    # -------------------------------------------------------------------------------------------------------
    runParser = subparsers.add_parser("run", help="run a set of tests on each of a set of cofigurations")

    # ... tests
    testGroup = runParser.add_mutually_exclusive_group()
    testGroup.add_argument("tests",    nargs="?",       type=str, default="all",     help="test-spec for the set of test cases to be run")
    testGroup.add_argument("--tests",            "-t",  type=str, default="all",     help="test-spec for the set of test cases to be run")

    # ... configs
    runParser.add_argument("--configs",          "-c",  type=str, default="default", help="build-spec for the set of build configs on which to test")

    # ... hpctoolkits
    runParser.add_argument("--hpctoolkits",      "-H", type=str,  default="default",  help="paths to installations of hpctoolkit with which to test")

    # ... hpcrun/struct/prof params
    runParser.add_argument("--hpctoolkitparams", "-p", type=str,  default="default",  help="parameters for the programs in hpctoolkit with which to test")

    # ... workspace 
    runParser.add_argument("--workspace",        "-w", type=str,  default="default",  help="where to create run directory for this run")

    # ... repetitions 
##  runParser.add_argument("--numrepeats",       "-n", type=int,  default=1,          help="number of times to repeat each test run")

    # ... report spec
    runParser.add_argument("--report",           "-r", type=str,  default="default",  help="details of report to be produced")
    
    # ... sort spec
    runParser.add_argument("--sort",             "-s", type=str,  default="default",  help="sequence of dimensions to sort report by")
                                                 #                                         "tests, "configs", "hpctoolkits", "hpctoolkitparams"
    
    # ... options       
    _addOptionArgs(runParser)
    # -------------------------------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------------------------------
    # hpctest report [ workspace | --workspace workspace ] [ --report reportspec ] [ --sort sortspec ] <options>
    # -------------------------------------------------------------------------------------------------------
    reportParser = subparsers.add_parser("report", help="print report summarizing a workspace")

    # ... workspace
    workGroup = reportParser.add_mutually_exclusive_group()
    workGroup.add_argument("workspace", nargs="?", type=str, default="default",  help="path to workspace to report on")
    workGroup.add_argument("--workspace", "-w",    type=str, default="default",  help="path to workspace to report on")

    # ... report spec
    reportParser.add_argument("--report", "-r",    type=str, default="default", help="details of report to be produced")
    
    # ... sort spec
    reportParser.add_argument("--sort",   "-s",    type=str, default="default", help="sequence of dimensions to sort report by")
    
    # ... options
    _addOptionArgs(reportParser)
    # -------------------------------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------------------------------
    # hpctest clean [ --all | [-w|--workspace  [workspace] ] [-t|-tests] [-d|--dependencies] ]   <options>
    # -------------------------------------------------------------------------------------------------------
    cleanParser = subparsers.add_parser("clean", help="clean up by deleting unwanted workspaces")

    # ... workspace
    cleanParser.add_argument("--workspace",    "-w", type=str, nargs="?", const="<default>", help="delete study directories from workspace")

    # ... tests
    cleanParser.add_argument("--tests",        "-t", action="store_true", help="uninstall built tests")

    # ... dependencies
    cleanParser.add_argument("--dependencies", "-d", action="store_true", help="uninstall packages built to satisfy tests' dependencies")

    # ... all
    cleanParser.add_argument("--all",          "-a", action="store_true", help="clean workspace, tests, and dependencies")
    
    # ... options
    _addOptionArgs(cleanParser)
    # -------------------------------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------------------------------
    # hpctest spack <cmd>
    # -------------------------------------------------------------------------------------------------------
    spackParser = subparsers.add_parser("spack", help="run a Spack command with hpctest's private Spack")
    spackParser.add_argument('spackcmd', nargs=argparse.REMAINDER)
    
    # ... options
    _addOptionArgs(spackParser)
    # -------------------------------------------------------------------------------------------------------


    # -------------------------------------------------------------------------------------------------------
    # hpctest _miniapps <options>
    # -------------------------------------------------------------------------------------------------------
    miniappsParser = subparsers.add_parser("miniapps", help="find all builtin miniapp packages and add test cases for them to tests/miniapp")
    
    # ... options
    _addOptionArgs(miniappsParser)
    # -------------------------------------------------------------------------------------------------------


    # parse the command line
    args = parser.parse_args()
    if args.options is None: args.options = {}          # can argparse do this automagically?
    common.options = args.options
    common.debugmsg("parsed args = {}".format(args))    # requires 'common.options' to be set

    return args


def _addOptionArgs(subparser):
    
    subparser.add_argument("--quiet",      "-q",  dest="options", action="append_const", const="quiet",      help="run silently")
    subparser.add_argument("--verbose",    "-v",  dest="options", action="append_const", const="verbose",    help="print additional details as testing is performed")
    subparser.add_argument("--debug",      "-D",  dest="options", action="append_const", const="debug",      help="print debugging information as testing is performed")
    subparser.add_argument("--force",      "-F",  dest="options", action="append_const", const="force",      help="do not ask for confirmation and ignore errors")
    subparser.add_argument("--traceback",  "-T",  dest="options", action="append_const", const="traceback",  help="print stack traces with error messages")
    subparser.add_argument("--nochecksum", "-C",  dest="options", action="append_const", const="nochecksum", help="ignore checksum of 'tests' directory tree")
    

def execute(args):
    # perform the requested operation by calling methods of HPCTest
    # TODO: figure out how to dispatch on subcommand so can implement 'hpctest clean'

    global tester
    from collections import OrderedDict
    from os.path import join
    from common import options, yesno

    if args.subcommand == "run":
        
        dims = OrderedDict()
        if args.tests != "default":
            dims["tests"] = args.tests
            del args.tests
        if args.configs != "default":
            dims["configs"] = args.configs
            del args.configs
        if args.hpctoolkits != "default":
            dims["hpctoolkits"] = args.hpctoolkits
            del args.hpctoolkits
        if args.hpctoolkitparams != "default":
            dims["hpctoolkitparams"] = args.hpctoolkitparams.replace("_", "-").replace(".", " ")  # undo the workaround for argparse fail on quoted args
            del args.hpctoolkitparams
        workspace  = args.workspace if args.workspace != "default" else None; del args.workspace
        numrepeats = 1  ## args.numrepeats
        otherargs  = args
        reportspec = args.report if args.report != "default" else "all"
        sortKeys   = [ key.strip() for key in (args.sort).split(",") ] if args.sort != "default" else []
        tester.run(dims, args, numrepeats, reportspec, sortKeys, workspace)
        
    elif args.subcommand == "report":
        
        workspace  = args.workspace if args.workspace != "default" else None; del args.workspace
        reportspec = args.report if args.report != "default" else "all" 
        sortKeys   = [ key.strip() for key in (args.sort).split(",") ] if args.sort != "default" else []
        tester.report(workspace, reportspec, sortKeys)
        
    elif args.subcommand == "clean":    
        
        w = args.workspace
        t = args.tests
        d = args.dependencies
        
        if w or t or d:
            if args.all:
                infomsg("option '--all' may not be combined with other options, so is ignored")
        elif args.all:
            w = "<default>"
            t = True
            d = True
        else:
            w = "<default>"
            
        tester.clean(w, t, d)

        
    elif args.subcommand == "spack":
        
        tester.spack(" ".join(args.spackcmd))
        
    elif args.subcommand == "miniapps":
        
            tester.miniapps()
    else:
        
        fatalmsg("in main.execute, unexpected subcommand name")
    




if __name__ == "__main__": main()



