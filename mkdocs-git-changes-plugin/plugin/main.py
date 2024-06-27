import logging
from git import Repo
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin
import re

class GitChangesPlugin(BasePlugin):

    config_scheme = (
        ('reference_branch', config_options.Type(str, default='main')),
    )

    def __init__(self):
        self.log = logging.getLogger(f"mkdocs.plugins.{__name__}")

    def on_config(self, config):
        self.repo = Repo('.')        
        self.reference_branch = self.config['reference_branch']
        self.log.info(self.reference_branch)
        return config

    def on_page_markdown(self, markdown, page, config, files):
        self.log.info(page.file.src_path)

        current_branch = self.repo.active_branch.name
        if current_branch == self.reference_branch:
            return markdown       

        diff = self.repo.git.diff(self.reference_branch, '-U65535', '--', page.file.src_path, word_diff=True)
        if not diff.strip():  # Check if diff is empty
            return markdown        

        markdown = self.wrap_added_words(diff)
        markdown = self.wrap_removed_words(diff)

        self.log.info("------------- markdown --------------")
        self.log.info(markdown)
        self.log.info("------------- ^ markdown ^ --------------")

        return markdown

    def wrap_added_words(self, diff):
        # Process the markdown content and wrap the added words in an HTML tag
        added_word_pattern = re.compile(r'\{\+(.*?)\+\}')
        markdown = re.sub(added_word_pattern, r'<strong style="color:green;">\1</strong>', diff)
        return markdown

    def wrap_removed_words(self, diff):
        # Process the markdown content and wrap the removed words in an HTML tag
        removed_word_pattern = re.compile(r'\[-(.*?)-\]')
        markdown = re.sub(removed_word_pattern, r'<strong style="color:red;">\1</strong>', diff)
        return markdown