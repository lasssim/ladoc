import logging
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin
import subprocess

class GitBranchPlugin(BasePlugin):

    config_scheme = (
        ('main_branch', config_options.Type(str, default='main')),
    )
    def __init__(self):
        self.log = logging.getLogger(__name__)

    def on_config(self, config):
        self.trace(self.config)

        try:
            current_branch_name = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
            config['extra']['git_current_branch'] = current_branch_name
            adr_branches = subprocess.check_output(['git', 'branch', '-r', '--list', '*/ADR/*']).decode('utf-8').strip().split('\n')
            adr_branches = [branch.replace('*', '').replace('origin/', '').strip() for branch in adr_branches]
            # Ensure "main" is in the list
            if self.config['main_branch'] not in adr_branches:
                adr_branches.insert(0, self.config['main_branch'])
            config['extra']['git_branches'] = adr_branches
            config['extra']['git_main_branch'] = self.config['main_branch']
        except subprocess.CalledProcessError:
            # Not a git repository, do nothing
            pass

        return config
    

    def format_trace(self, *args):
        """
        General purpose print function, as trace,
        for the mkdocs-macros framework;
        it will appear if --verbose option is activated
        """
        first = args[0]
        rest = [str(el) for el in args[1:]]
        text = "[%s] - %s" % (self.TRACE_PREFIX, first)
        return ' '.join([text] + rest)

    import logging

    # ------------------------------------------
    # Trace and debug
    # ------------------------------------------
    TRACE_PREFIX = 'git_branch' 

    # Set up the logger
    LOG = logging.getLogger(f"mkdocs.plugins.{TRACE_PREFIX}")

    # Define the trace function
    def trace(self, message, level='INFO'):
        """
        General purpose print function, as trace,
        for the mkdocs-macros framework;
        it will appear unless --quiet option is activated.

        The level is 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'.
        """
        # Get the logging level
        log_level = getattr(logging, level.upper(), None)
        if not isinstance(log_level, int):
            raise ValueError(f"Invalid log level: {level}")

        # Log the message
        self.LOG.log(log_level, self.format_trace(message)) 