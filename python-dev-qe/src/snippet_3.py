"""
Codes on this file are only for demonstration purpose and might not be 
executable.

:topic Pyhton pytest
:level basic

"""

import pytest
from tests.util import run, is_installed, get_docker_image_id, yum_remove
from tests.util import yum_install, get_rpm_version, pull_docker_image

_docker = is_installed("docker")
@pytest.mark.skipif(_docker is None, reason="docker not installed")
class TestDockerValidateBugz(object):
    def test_bz_1501552(self):
        """
        https://bugzilla.redhat.com/show_bug.cgi?id=1501552
        
        Check for correct message output when python-docker-py package
        is not installed in the system
        
        @cmd: insights-client --analyze-image-id ddb20f8825f0
        """
        # check for exists docker image
        image_id = get_docker_image_id()
        if not image_id:
            pull_docker_image()
        image_id = get_docker_image_id()            
        assert image_id, "Can not find a docker image in the system"

        # remove python-docker-py from system to simulate message
        package = "python-docker-py"
        try:
            get_rpm_version(package)
            yum_remove(package)
            print "%s has been removed" % package
        except:
            print "%s is not installed" % package
        
        # check for stdout msg for cmd
        cmd = "insights-client --analyze-image-id %s" % image_id
        rs = run(cmd)
        print rs
        result = []
        duplicity = False
        msg = ("The docker-py Python libraries do not appear to be installed. Please install the python-docker-py RPM package.")
        stdout_msg = []
        # convert stdout into a list for better handling
        for line in rs['stdout'].split("\n"):
            if len(line) > 0:
                stdout_msg.append(line)
        
        for pos,user_msg in enumerate(stdout_msg):
            print "%s | %s" % (pos, user_msg)
            # user msg must match with client stdout
            if msg not in user_msg:
                result.append("%s, not found expected msg in stdout" % pos)
            # check for duplicity
            if pos > 0 and msg in user_msg:
                duplicity = True
        
        assert rs['rc'] == 1, "client didnt halt"
        assert len(result) == 0, "stdout doenst match with expected msg" 
        assert duplicity == False, "stdout msg duplicated"

    def test_bz_1501556(self):
        """
        https://bugzilla.redhat.com/show_bug.cgi?id=1501556
        
        insights-client continues to execute after it couldn't find a 
        matching image, causing ugly output and errors to be printed.
                
        @cmd: insights-client --analyze-image-id fakeimgid123
        """
        # install python-docker-py from system to simulate message
        package = "python-docker-py"
        try:
            get_rpm_version(package)
            print "%s is already installed" % package
        except:
            yum_install(package)
            print "%s has been installed" % package
        
        msg = "There was an error collecting targets. No image or container was found matching this ID."
        # check for stdout msg for cmd
        cmd = "insights-client --analyze-image-id fakeimgid123"
        rs = run(cmd)
        print rs
        cmd_output = []
        # convert stdout into a list for better handling
        for line in rs['stderr'].split("\n"):
            if len(line) > 0:
                cmd_output.append(line)
        
        result = []
        for pos,line in enumerate(cmd_output):
            # expected message and nothing else
            if pos == 0 and msg not in line:
                result.append("msg expected not found in stdout")
            # not expected messages
            if "AttributeError" in line \
            or "Fatal error" in line \
            or "Traceback" in line \
            or "ERROR" in line:
                result.append("msg not expected found in stdout")
            
        assert len(result) == 0, result
