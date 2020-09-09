#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Multiprocess job handler with disaster recovery 

TODO:

disaster_proof: have 2 classes one diaster proof ther other xmlrpc 
with different helper classes
"""

# ===========================================================================
# module export and import
# ===========================================================================

# version
__version__ = "$Revision: 0.1.2011-10-11 $"

# export
__all__ = [
    'WorkerError',
    'WorkerInitError',
    'WorkerExecError',
    'Worker',
]

# standard import
import glob
import datetime
import time
import logging
import signal
log = logging.getLogger( __name__ )

# extra import
import multiprocessing
import validate
import pt.proc.ps
import pt.config
import pt.files.dir 


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
        * job status is stored in memory (accessible via xmlrpc) or in file 
          system (disaster-proof)
          > disaster - proof: pid files are stored in sub dirs of pid_dir
          > xmlrpc: call status() method
            waiting : new jobs
            running : jobs beeing executed right now
            stopped : jobs stopped, waiting for re-enqueueing via restart command
            finished: successfully executed jobs
            failed  : failed jobs
        * jobs are executed fifo, ( sorted by enqueue date )
    FEATURES
    METHODS
        start(): enqueue single job or start a dictionary of jobs
        stop()
        clear()
        status()
        remove_job()
        append_job()
    PARAMETERS
        * pid_dir = None,
          <some path>: job status is handled in file system. This is very 
            transparent but slower then memory handler. Enqueuing jobs while
            worker is running already is possible only wiht oid_dir beeing set.
            This mode is disaster-proof operation mode
          None: keeping job status in memory where status is lost after e.g. 
          system breakdown
        * jobs = {},     
          Array of jobs: functions or methods, their arguments to run
            jobs = {
                name: { function : '', arguments: []}
            }
        * max_jobs = 10,
          How much jobs can be started in parallel, 0: start all jobs parallel
        * max_cpus = None, 
          Number of cpu's to use, standard is to use all available cores 
        * check_interval how long to wait between checking number of parallel 
          jobs currently running, default: 300 (seconds = 5 minutes)
    EXCEPTIONS
    LOGGING
    EXAMPLE
    """
    # class constants:
    WAITING  = 'waiting'
    RUNNING  = 'running'
    STOPPED  = 'stopped'
    FINISHED = 'finished'
    FAILED   = 'failed' 

    ALL_QUEUES     = [ WAITING, RUNNING, STOPPED, FINISHED, FAILED ]

    CHECK_INTERVAL = 2  # seconds

    # -----------------------------------------------------------------------
    def __init__(self, 
    # -----------------------------------------------------------------------
        pid_dir  = None,
        worker_name = None,
        jobs = {}, #  name: { function : '', arguments: []}
        max_jobs = 10,
        max_cpus = None, 
        check_interval = CHECK_INTERVAL,
        ):

        # store input in instance
        self.jobs = jobs
        self.max_jobs = validate.is_integer(max_jobs, 0)
        self.pid_dir  = pid_dir

        self.check_interval = validate.is_integer( check_interval, 1 )

        self._setup_queue_storage()
        self.running_jobs = 0
        self.childs       = {}  # child process storage

        if not pid_dir:
            log.warning( "OPERATION without not pid dir is not testet, yet!" )



    # -----------------------------------------------------------------------
    # main methods
    # -----------------------------------------------------------------------
    
    def start(self, name=None, job=None):
        """
        DESCRIPTION
            Run job functions in parallel until all jobs are
            finished. 
            Runs clear() and restart() at start, see descriptions 
            there
            If a single job is given, add this one to runnning/ waiting queue
            Job names must be unique.
        PARAMETERS
        RETURN VALUES
            * If worker is running already, return None
            * When all jobs are finished without errors, return True
            * When all jobs are finished but there were errors, return False
        EXCEPTIONS
        """

        if   job and name:
            if self.pid_dir:
                self._enqueue_job( name, job )
                return self._start_worker()
            else:
                raise WorkerInitError(
                    "Running in memory-queue mode, jobs must be added "
                    "at class initialisation. Alternatively, define a "
                    "pid_dir and run diaster-proof mode"
                )

        elif job  or name:
            raise WorkerInitError(
                "start() called with name or worker parameter. Need both for "
                "enqueueing single job!"
            )
        else:
            # start worker loop
            if self._worker_running():
                raise WorkerInitError(
                    "Found running jobs in queue, looks like worker "
                    "is doing already"
            )
            self.clear()
            for job_name in self.jobs.keys():
                self._enqueue_job( job_name, self.jobs[job_name] )
            self.restart()


    def stop(self, job_name=None):
        """
        DESCRIPTION
            Stop executing all jobs or single job, if given. Running job 
            pid markers are beeing moved to "stopped" pid dir. Via restart(), 
            this jobs will be started first (before "waiting" jobs)
        PARAMETERS
        RETURN VALUES
        EXCEPTIONS
        """
        queue = self.RUNNING

        if job_name:
            self._set_stopped( queue, job_name )
        else:
            for job_name in self._iget_job_names(queue):
                self._set_stopped( queue, job_name )


    def restart(self):
        """
        DESCRIPTION
            Reload stored job queue, start all jobs wich are in running, 
            stopped or waiting queue ( in this order ). See stop()
        PARAMETERS
        RETURN VALUES
        EXCEPTIONS
        """

        if self._worker_running():
            raise WorkerInitError(
                "Found running jobs in queue, looks like worker "
                "is doing already"
           )

        for queue in [ self.RUNNING, self.STOPPED ]:
            for job_name in self._iget_job_names(queue):
                if self.running_jobs <= self.max_jobs:
                    log.debug( 
                        'Re - starting job "%s" found in "%s" queue'
                        % (job_name, queue)
                    )
                    self._set_running( queue, job_name )
                else:
                    log.debug( 
                        'Set job "%s" found in "%s" queue to queue "%s"'
                        % (job_name, queue, self.WAITING)
                    )
                    self._move_queue( job_name, queue, self.WAITING )

        if self._start_worker():
            log.info( "Finished all jobs, exiting!" )
        else:
            log.error( 
                "Finished job, there where errors - "
                "see '%s'" % ( self.pid_dir + os.sep + self.FAILED  ) 
            )
                
    def clear(self):
        """
        DESCRIPTION
            Clear all waiting, stopped, finished and failed job queues. 
            Running jobs are left where they are. 
        PARAMETERS
        RETURN VALUES
        EXCEPTIONS
        """
        for queue in [self.WAITING, self.RUNNING, self.FINISHED, self.FAILED]:
            for job_name in self._iget_job_names(queue):
                self._remove_job( queue, job_name )

    def status(self, job_name=None):
        """
        DESCRIPTION
            Show all job queues
        PARAMETERS
        RETURN VALUES
        EXCEPTIONS
        """

        # single job's status is requestet
        if job_name:
            queue = self._get_job_queue( job_name)
            if queue:
                print 'Job is enqueued in "%s"' % queue
            else:
                print 'Job is not in enqueued'

        # display all jobs
        else:
            no_jobs = True
            for queue in self.ALL_QUEUES:
                for job_name in self._iget_job_names(queue):
                    no_jobs = False
                    job = self._read_job(queue, job_name )
                    print "%-10s : %-10s " % ( queue.upper(), job_name ),
                    # print last actions's date
                    if queue == self.WAITING:
                        date_key = 'enqueue_date'
                        action_string = 'enqueued'
                    else:
                        date_key = "%s_date" % queue
                        action_string = '%s' % queue
                    date_string = str(job[date_key]).split('.')[0]
                    print "(%-9s since %s)" % (action_string, date_string )
            if no_jobs:
                print "There are no jobs in queues."

    # -----------------------------------------------------------------------
    # _helper methods, mainly dealing with single jobs
    # -----------------------------------------------------------------------


    # --------------------------
    def _start_worker(self):
    # --------------------------
        """
        DESCRIPTION
            Check if there are running jobs 
            * if not, start executing waiting jobs and wait until this jobs 
            are finished. Jobs get moved between queues according to status
            * if yes, worker must be running already - do nothing then
            * On errors, move jobs to failed queue
        PARAMETERS
        RETURN VALUES
            * When all jobs are finished without errors, return True
            * When all jobs are finished but there were errors, return False TODO

        EXCEPTIONS
        """

        log.debug( "Starting worker loop" )

        # start all jobas one after the other, wait until finished
        while True:
            log.debug( "Checking jobs in running and waiting queue")

            jobs_left = False
            for job_name, job in self._iget_sorted_jobs( self.RUNNING ):
                jobs_left = True
                if self._is_running( job ):
                    continue
                else:
                    # job has finished
                    self.running_jobs -= 1
                    if self.running_jobs < 0:
                        self.running_jobs = 0

                    # handle exitcode: store, move job to queue
                    ec = self.childs[job_name].exitcode
                    if ec == 0:
                        target_queue = self.FINISHED
                        job['%s_date' % self.FINISHED ] = datetime.datetime.now()
                    else:
                        target_queue = self.FAILED
                        job['%s_date' % self.FAILED   ] = datetime.datetime.now()

                    job['exitcode'] = ec
                    self._save_job( self.RUNNING, job_name, job )
                    self._move_queue( job_name, self.RUNNING, target_queue )

            for job_name, job in self._iget_sorted_jobs( self.WAITING ):
                jobs_left = True
                if self.running_jobs <= self.max_jobs:
                    # restart job
                    self._set_running( self.WAITING, job_name, job )
                else:
                    # wait till some jobs are finished
                    break

            # check if there are any jobs left
            if jobs_left:
                time.sleep( self.check_interval )
                continue
            else:
                return True

    # --------------------------
    def _enqueue_job(self, name, data ):
    # --------------------------
        """
        DESCRIPTION
            Analyse job data, check if this job is present in any
            queue already and append it to waiting queue, if not
        """

        for queue in self.ALL_QUEUES:
            for job_name in self._iget_job_names( queue):
                if name == job_name:
                    raise WorkerInitError(
                        "Job name '%s' is not unique, found same name "
                        'in "%s" queue' % (name, queue)
                    )


        queue = self.WAITING
        log.debug( "Enqueueing job '%s' to waiting queue" % name )

        # init config
        if self.pid_dir:
            queue_dir = self.pid_dir + os.sep + queue
            pid_file  = queue_dir + os.sep + name
            cfg = pt.config.ConfigFile(pid_file)
        else:
            cfg = pt.config.Config()

        # populate config, check items
        try:
            cfg['function']     = validate.is_string( data['function'])
            cfg['arguments']    = validate.is_list(data['arguments'] )
        except validate.ValidateError, emsg:
            raise WorkerInitError(
                "Could not enqueue job '%s', error '%s'" 
                % (name, emsg)
            )
        cfg['enqueue_date']         = datetime.datetime.now()

        self._save_job( queue, name, cfg )



    # --------------------------
    def _set_running(self, queue, job_name, job = None):
    # --------------------------
        """ Start job """

        # move queue
        log.debug( "Starting job '%s'" % job_name )

        if not job:
            job = self._read_job( queue, job_name )
  
        module = sys.modules[__name__]
        function_reference = getattr( module, job['function'] )

        child = multiprocessing.Process(
            target = function_reference,
            args   = job['arguments'],
            name   = job_name,
        )
        child.start()

        # store config
        self.childs[job_name] = child 
        job['pid'] = child.pid
        job[ '%s_date' % self.RUNNING ] = datetime.datetime.now()

        self._save_job( self.RUNNING, job_name, job )

        self._move_queue( job_name, queue, self.RUNNING )
        self.running_jobs += 1

    # --------------------------
    def _set_stopped(self, queue, job_name):
    # --------------------------
        """
        Stop running process
        """
        log.debug( "Stopping job '%s' " % job_name )

        job = self._read_job( queue, job_name )
        try:
            child = self.childs[job_name]
        except KeyError:
            # child does not exist in internal job list, kill system process list
            log.debug( 'Killing system process %s' % job['pid'])
            os.kill(int(job['pid']), signal.SIGHUP)
            time.sleep(0.1)
            os.kill(int(job['pid']), signal.SIGKILL)

        else:
            log.debug( 'Terminating internal job %s, pid %s' % (job_name, job['pid'] ))
            # update process status
            child.is_alive()
            # terminate child
            child.terminate()
            child.join()

        job[ '%s_date' % self.STOPPED ] = datetime.datetime.now()
        self._save_job( queue, job_name, job )
        self._move_queue( job_name, queue, self.STOPPED )

        self.running_jobs -= 1
        if self.running_jobs < 0:
            self.running_jobs = 0

    # --------------------------
    def _worker_running(self):
    # --------------------------
        """
        Return True if worker loop is running already, False otherwise
        """
        # check if there are running jobs, already
        for job_name in self._iget_job_names( self.RUNNING ):
            job = self._read_job(self.RUNNING, job_name)
            if self._is_running( job ):
                return True
        else:
            return False

    # --------------------------
    def _is_running( self, job):
    # --------------------------
        """
        Test if a job is currently running
        """
        # check if job was started in this loop ...
        for child in self.childs.keys():
            # close zombie childs
            self.childs[child].is_alive()

            # check if child is running, really
            if self.childs[child].pid == job['pid']:
                if self.childs[child].is_alive():
                    return True
                else: 
                    return False
        else:
            # or exists in systems process list
            for process in pt.proc.ps.get_processes():
                try:
                    if int(process.pid) == int(job['pid']):
                        return True
                except KeyError:
                    return False
            else:
                return False

    # --------------------------
    def _move_queue(self, job_name, source_queue, target_queue):
    # --------------------------
        """
        DESCRIPTION
            Move job to given target_queue
        PARAMETERS
        """
        log.debug( 
            'Moving job "%s" from "%s" queue to "%s" queue' 
            % ( job_name, source_queue , target_queue)
        )

        if self.pid_dir:
            source_queue_dir = self.pid_dir + os.sep + source_queue
            target_queue_dir = self.pid_dir + os.sep + target_queue

            source_pid_file  = source_queue_dir + os.sep + job_name
            target_pid_file  = target_queue_dir + os.sep + job_name
            os.rename( source_pid_file, target_pid_file )
        else:
            self.queues[target_queue][job_name] = self.queues[source_queue][job_name]
            del self.queues[source_queue][job_name]

    # --------------------------
    def _remove_job(self, queue, job_name):
    # --------------------------
        """
        DESCRIPTION
            Remove single job from queue
        PARAMETERS 
            queue, job name
        RETURN VALUE
        """
        if self.pid_dir:
            queue_dir = self.pid_dir + os.sep + queue
            pid_file  = queue_dir + os.sep + job_name
            log.debug( "Removing pid file '%s'" % pid_file)
            os.unlink( pid_file )
        else:
            log.debug ( 
                """Removing job '%s' from "%s" queue""" 
                % (job_name, queue) 
            )
            del self.queues[queue][job_name]


    # --------------------------
    def _save_job(self, queue, job_name, cfg ):
    # --------------------------
        """
        Helper: store cfg items to disc or memory
        """

        if self.pid_dir:
            cfg.write()
        else:
            self.queues[queue][name] = cfg


    # --------------------------
    def _read_job(self, queue, job_name):
    # --------------------------
        """
        Get job data from memory or job pid fiel, return data
        as configobj object
        """
        if self.pid_dir:
            queue_dir = self.pid_dir + os.sep + queue
            pid_file  = queue_dir + os.sep + job_name
            cfg = pt.config.ConfigFile(pid_file)
            cfg['enqueue_date'] = datetime.datetime.strptime(
                cfg['enqueue_date'], 
                "%Y-%m-%d %H:%M:%S.%f",
            )
            try:
                cfg['start_date'] = datetime.datetime.strptime(
                    cfg['start_date'], 
                    "%Y-%m-%d %H:%M:%S.%f",
                )
            except KeyError:
                # not started yet, no worries
                pass
        else:
            cfg = self.queues[queue][job_name]
        validate.is_string     ( cfg['function']     )
        validate.is_list( cfg['arguments']    )
        return cfg

    # --------------------------
    def _iget_job_names(self, queue):
    # --------------------------
        """
        DESCRIPTION
            List all jobs in given queue
        PARAMETERS
            queue name
        RETURN VALUE
            dictionary of jobs
        """
        if self.pid_dir:
            queue_dir = self.pid_dir + os.sep + queue
            for job_file in glob.iglob( "%s/*" % queue_dir ):
                yield os.path.basename(job_file)
        else:
            for job in self.queues[queue].keys():
                yield job

    # --------------------------
    def _iget_sorted_jobs( self, queue):
    # --------------------------
        """
        Return generator for jobs in queue, sorted by enqueue date
        """
        all_dates = []
        jobs_by_date = {}
        for job_name in self._iget_job_names(queue):
            job = self._read_job( queue, job_name )
            jobs_by_date[ job['enqueue_date'] ] = (job_name, job )
            all_dates.append( job['enqueue_date'] )

        for date in sorted( all_dates ):
            yield jobs_by_date[date]

    # --------------------------
    def _get_job_queue(self, job_name):
    # --------------------------
        """
        DESCRIPTION
            Check if job_name is enqueued in any queue, already
        PARAMETERS
            job_name
        RETURN VALUES
            * queue for which given job_name is in,
            * False if this job is not in any queue
        """
        for queue in self.ALL_QUEUES:
            for job_search_name in self._iget_job_names(queue):
                if job_name == job_search_name:
                    return queue
        else:
            return False

    # --------------------------
    def _setup_queue_storage(self):
    # --------------------------
        """
        DESCRIPTION
            Depending on self.pid_dir, create queues in file system
            or memory
        PARAMETERS
            self.pid_dir
        EXCEPTIONS
            WorkerInitError: setting up job file dir went wrong
        """

        if self.pid_dir:
            for queue in self.ALL_QUEUES:
                try:
                    dir_name = self.pid_dir + os.sep + queue
                    pt.files.dir.create( dir_name )
                except (pt.files.dir.FsDirError, TypeError), emsg:
                    try:
                        raise WorkerInitError(
                            "Could not create jobs pid directory '%s':\n%s" 
                            % ( dir_name , emsg)
                        )
                    except UnboundLocalError:
                        raise WorkerError(
                            "Specify jobs pid directory pid_dir!"
                        )

        else:
            self.queues = {}
            for queues in self.ALL_QUEUES:
                self.queues['queue'] = {}

# ---------------------------------------------------------------------------
# error classes                                                          
# ---------------------------------------------------------------------------
class WorkerError(BaseException):
    """General error starting or running child process """
class WorkerInitError(WorkerError):
    """Error running background """
class WorkerExecError(WorkerError):
    """Error running backgronud """


# ===========================================================================
# tests and example invocation                                           
# ===========================================================================

def funcy(delay):
   # raise WorkerError()
    time.sleep(float(delay))
    print "HAAAAALLLLLLOOOO"
    return
   # sys.exit(0)

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

    #w = Worker(pid_dir='/home/gunnar/w1')
    jobs = {
        'job1': {
            'function' : 'funcy',
            'arguments' : [20],
        },
        'job2': {
            'function' : 'funcy',
            'arguments' : ['hallo'],
        },
    }
    w = Worker(pid_dir='/home/torpedo/w1', jobs=jobs)
    w.restart()
    w.status()
#    w.stop()
