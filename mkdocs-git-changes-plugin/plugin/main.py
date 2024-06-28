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

        if self.current_branch_name() == self.reference_branch:
            return markdown       

        diff = self.diff(page)
        if not diff.strip():
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
    
    def current_branch_name(self):
        branch_name = None

        if not self.repo.head.is_detached:
            branch_name = self.repo.active_branch.name

        if not branch_name:
            branch_name = os.getenv('CI_COMMIT_REF_NAME')

        if not branch_name:
            raise ValueError("Branch name could not be determined from active branch or CI_COMMIT_REF_NAME environment variable.")

        return branch_name

    def diff(self, page):
        self.fetch_reference_branch_if_not_locally_available()
        return self.repo.git.diff(self.reference_branch, '-U65535', '--', page.file.src_path, word_diff=True)

    def fetch_reference_branch_if_not_locally_available(self):
        # print status of the repo
        print("Repo status")
        self.log.info(self.repo.git.status('-v'))
        try:
            ret = self.repo.git.rev_parse('--verify', '-v', self.reference_branch)
            print("Repo verify")
            self.log.info(ret)
        except:
            ret = self.repo.git.fetch('origin', '-v', self.reference_branch)
            print("Fetch reference branch")
            self.log.info(ret)
            print("Repo verify")
            self.log.info(self.repo.git.rev_parse('--verify', '-v', self.reference_branch))