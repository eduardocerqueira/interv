"""
Codes on this file are only for demonstration purpose and might not be 
executable.

:topic Pyhton in general
:level basic

"""

def run(cmd, fatal=None, cwd=None, stdout=PIPE, stderr=PIPE,
                    env=None):
    """Run a shell command subprocess call using Popen.

    :param cmd: (str) Command to run
    :param fatal: (boolean) Whether to raise exception with failure
    :param cwd: (str) Directory path to switch to before running command
    :param stdout: (int) Pass subprocess PIPE if you want to pipe output
           from console
    :param stderr: (int) Pass subprocess PIPE if you want to pipe output
           from console
    :return: (dict) The results from subprocess call
    """
    results = {}
    proc = Popen(cmd, shell=True, stdout=stdout, stderr=stderr, cwd=cwd,
                 env=env)
    output = proc.communicate()

    results['rc'] = proc.returncode
    results['stdout'] = output[0]
    results['stderr'] = output[1]

    if proc.returncode != 0:
        LOG.debug(output)
        if fatal:
            raise Exception(results['stderr'])
        else:
            LOG.error(results['stderr'])

    return results

def pull_docker_image():
    """
    Pull a valid docker image to local system to be used by insights-client
    during tests execution

    :return rc code (str)
    """
    cmd = "docker pull eduardomcerqueira/paws:0.3.8.1-centos-latest"
    rs = run(cmd)
    return rs['rc']

def delete(lst_files):
    """
    Delete files from local file system
    
    :param lst_files (list) absolute path
    :return (boolean)  
    """
    try:
        for local_file in lst_files:
            if exists(local_file):
                remove(local_file)
    except IOError as ex:
        print ex
    
    return True




