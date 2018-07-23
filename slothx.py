# !/usr/bin/env python
# coding        = utf-8
# __copyright__ = 'HK JiuLing'
# __author__    = 'HongKong JiuLing'
# __project__   = 'Video Structuring"

import sys
from os.path import dirname, realpath
sys.path.insert(1, dirname(dirname(dirname(realpath(__file__)))))
from PyQt4.QtGui import QApplication
from sloth.core.labeltool import LabelTool
from sloth.conf import config

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName(config.ORGANIZATION_NAME)
    app.setOrganizationDomain(config.ORGANIZATION_DOMAIN)
    app.setApplicationName(config.APP_NAME)

    labeltool = LabelTool()
    labeltool.execute_from_commandline(sys.argv)

    labeltool.logger.info("execute_from_commandline returned")
    exitcode = app.exec_()
    labeltool.logger.info("exit from application with exitcode {} ...".format(exitcode))
    
    sys.exit(exitcode)

