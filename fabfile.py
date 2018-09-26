import os ,re
from datetime import datetime

from fabric.api import *


env.user='ubuntu'

env.sudo_user='root'
env.hosts=['54.185.11.253']
env.key_filename='d:\iCloudDrive\wingolol.pem'


mysql_user='wing'

mysql_passwd='wing'

_TAR_FILE= 'dist-webapp.tar.gz'

def build():
        includes=['static','templates','favicon.ico','*.py','table2.sql']
        excludes=['test*.py']
        local('rm -f dist/%s' % _TAR_FILE)
        with lcd(os.path.join(os.path.abspath('.'),'www')):
                  cmd=['tar','-czvf','../dist/%s' % _TAR_FILE]
                  cmd.extend(['--exclude=%s' % ex for ex in excludes])
                  cmd.extend(includes)
                  local(' '.join(cmd))


_REMOTE_TMP_TAR='/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR='/home/ubuntu/srv/wing'

def deploy():
       newdir='www-%s' % datetime.now().strftime('%y-%m-%d-%H-%M-%S')

       run('rm -f %s' % _TAR_FILE)
       put('dist/%s' % _TAR_FILE,_REMOTE_TMP_TAR)
       with cd(_REMOTE_BASE_DIR):
            sudo('mkdir %s' % newdir)
       with cd('%s/%s' %(_REMOTE_BASE_DIR,newdir)):
             sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)
       with cd(_REMOTE_BASE_DIR):
             sudo('rm -rf www')
             sudo('ln -s %s www  ' % (newdir))

       with settings(warn_only=True):
              sudo('supervisorctl stop pythonweb')
              sudo('supervisorctl start pythonweb')
              sudo('/etc/init.d/nginx reload')



