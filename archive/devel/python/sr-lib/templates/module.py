#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Multiprocess job handler with disaster recovery """

# ===========================================================================
# module export and import
# ===========================================================================

# version
__version__ = "$Revision: 0.1.2011-10-11 $"

# export
__all__ = [
    'Module',
    'WorkerError',
    'Worker',
]

# standard import
import logging
log = logging.getLogger( __name__ )

# extra import
import validate # from python-configobj

# ===========================================================================
# classes 
# ===========================================================================

#----------------------------------------------------------------------------
# main class                                                             
#----------------------------------------------------------------------------
class Worker:
    """
    DESCRIPTION
        multiprocess job handler with disaster recovery based on multiprocess
        lib. Multiple functions may be called in parallel.
        * processes: more overhead than threading but able to access multi-core 
          capabilities. Jobs run transparently in os via process list (ps auxf) 
          and pid files in pid_dir
        * depending on job state, pid files are stored in sub dirs of pid_dir:
            waiting : new jobs
            running : jobs beeing executed right now
            stopped : jobs stopped, waiting for re-enqueueing via restart command
            finished: successfully executed jobs
            failed  : failed jobs
    FEATURES
    METHODS
        start()
        stop()
        clear()
        status()
        remove_job()
        append_job()
    PARAMETERS
        * disaster_proof = True, 
          True: job status is handled in file system this is very transparent 
          but slower then 
          False: keeping job status in memory where status is lost after e.g. 
          system breakdown 
          jobs
        * jobs = {},     
          Array of jobs: functions, their arguments to run and what to grep 
          for in system's process list
            jobs = {
                name: { function : '', arguments: [], proc_strings: []}
            }
        * max_jobs = 10,
          How much jobs can be started in parallel check_intervall How long
          to wait between job status checks 
        * max_cpus = None, 
          Number of cpu's to use, standard is to use all available cores 
        * pid_dir = None,
          Where to store pid files, standard is /var/run/worker/<job name>   
    EXCEPTIONS
    LOGGING
    EXAMPLE
    """
    # class constants:
    CONST = CONSTANT

    # -----------------------------------------------------------------------
    def __init__(self, 
    # -----------------------------------------------------------------------
        disaster_proof = True, 
        jobs = {},     
        max_jobs = 10,
        max_cpus = None, 
        pid_dir = None,
        ):

    # -----------------------------------------------------------------------
    # main methods
    # -----------------------------------------------------------------------

    def start(self):
        """
        DESCRIPTION
            Run functions max_jobs times in parallel until all jobs are
            finished. Clears and recreates all job queues at start.
        PARAMETERS
        RETURN VALUES
        EXCEPTIONS
        """

    def stop(self):
        """
        DESCRIPTION
        PARAMETERS
        RETURN VALUES
        EXCEPTIONS
        """




    # -----------------------------------------------------------------------
    # _helper methods
    # -----------------------------------------------------------------------
    def _get_proc_list(self):
        """
        DESCRIPTION
        PARAMETERS
        RETURN VALUES
        EXCEPTIONS
        """

# ---------------------------------------------------------------------------
# error classes                                                          
# ---------------------------------------------------------------------------
class WorkerError(BaseException):
    """General error starting or running child process """
#class WorkerInitError(BaseException):
#    """Error running backgronud """
#class WorkerExecError(BaseException):
#    """Error running background jobs """


# ===========================================================================
# tests and example invocation                                           
# ===========================================================================

if __name__ == "__main__":
    import sys
    import os
    import pt.terminal # flush buffers, colors, terminal size
    import pt.logger   # set up logger

    # initialize logger
    log = pt.logger.Logger(
        name         = None , # None = root logger
        level        = logging.DEBUG,  
        file_file    = None,      # None = no file logging
        file_level   = logging.DEBUG,         
    )
