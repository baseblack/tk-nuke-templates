"""
Copyright (c) 2012 Baseblack London, Ltd
----------------------------------------------------

Publishing and snapshotting in Nuke.

"""

import os
import sys
import nuke

import tank
from tank import TankError

class Templates(tank.platform.Application):

    def init_app(self):
        """
        Called when the app is being initialized
        """
        import tk_nuke_templates
        self.app_handler = tk_nuke_templates.AppHandler(self)

        self.engine.register_command("Search for a template...",
                                     self.app_handler.search_dialog,
                                     {"type": "template_menu"})

        self.engine.register_command("Publish as template...",
                                     self.app_handler.publish_dialog)

        self.engine.register_command("Help", self.documentation)


    def documentation(self):
        exec "import os; os.system('google-chrome https://sites.google.com/a/baseblack.com/tech/learning-resources/nuke/template-loader')"

