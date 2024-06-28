import logging
from git import Repo
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin
import re
import os

class GitChangesPlugin(BasePlugin):

    config_scheme = (
        ('reference_branch', config_options.Type(str, default='main')),
        ('doc_path', config_options.Type(str, default='.'))
    )

    def __init__(self):
        self.log = logging.getLogger(f"mkdocs.plugins.{__name__}")

    def on_config(self, config):
        self.reference_branch = self.config['reference_branch']
        self.doc_path = self.config['doc_path'].rstrip('/')

        self.repo = Repo(self.doc_path)
        self.repo.git.config('--global', '--add', 'safe.directory', self.doc_path)
 
        return config

    def on_page_markdown(self, markdown, page, config, files):
        self.log.info(page.file.src_path)

        current_branch = self.repo.active_branch.name
        if current_branch == self.reference_branch:
            return markdown       

        diff = self.repo.git.diff(self.reference_branch, '-U65535', '--', page.file.src_path, word_diff=True)
        if not diff.strip():  # Check if diff is empty
            return markdown        

        markdown = self.remove_diff_header(diff)
        markdown = self.wrap_page(markdown)
        markdown = self.wrap_changed_blocks(markdown)
        markdown = self.wrap_added_words(markdown)
        markdown = self.wrap_removed_words(markdown)

        return markdown

    def wrap_page(self, markdown):
        return f'<div class="git_changes_page" markdown="1">' + markdown + '</div>'

    def remove_diff_header(self, diff):
        # Remove the diff header
        diff = re.sub(r'diff --git.*?\n@@.*?@@\n', '', diff, flags=re.DOTALL)
        return diff
    

    def wrap_changed_blocks(self, diff):
        # Regular expression to match blocks enclosed in triple backticks that include changes
        pattern = r'(\{\+|\[-)?```.*?```(\+\}|\]-)?'
        
        # Function to wrap matched blocks in a div with a yellow background
        def wrap_block(match):
            block = match.group(0)
            # Remove word-diff wrappers
            block = re.sub(r'\{\+(.*?)\+\}', r'\1', block)
            block = re.sub(r'\[-(.*?)-\]', r'\1', block)
            return '<div class="git_changes_block_changed">\n' + block + '\n</div>'
        
        # Apply the regular expression and the wrap_block function to the diff
        diff = re.sub(pattern, wrap_block, diff, flags=re.DOTALL)
        
        return diff


    def wrap_added_words(self, diff):
        # Process the markdown content and wrap the added words in an HTML tag
        added_word_pattern = re.compile(r'\{\+(.*?)\+\}')
        markdown = re.sub(added_word_pattern, r'<span class="git_changes_added" markdown="1">\1</span>', diff)
        return markdown

    def wrap_removed_words(self, diff):
        # Process the markdown content and wrap the removed words in an HTML tag
        removed_word_pattern = re.compile(r'\[-(.*?)-\]')
        markdown = re.sub(removed_word_pattern, r'<span class="git_changes_removed" markdown="1">\1</span>', diff)
        return markdown