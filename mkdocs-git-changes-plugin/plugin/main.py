import logging
from git import Repo
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin
import re
import os
import markdown as md
from bs4 import BeautifulSoup

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
        markdown = self.remove_yaml_header(markdown)

        markdown = self.wrap_page(markdown)
        markdown = self.wrap_changed_blocks(markdown)
        markdown = self.wrap_added_headings(markdown)
        markdown = self.wrap_removed_headings(markdown)
        markdown = self.wrap_added_words(markdown)
        markdown = self.wrap_removed_words(markdown)

        self.log.info(markdown)
        return markdown

    def remove_yaml_header(self, markdown):
        # Regular expression to match the YAML header
        pattern = r'---\n(.*?)\n---\n'
        markdown_without_header = re.sub(pattern, '', markdown, flags=re.DOTALL)

        return markdown_without_header

    def wrap_page(self, markdown):
        # If there's no YAML header, wrap the whole content
        return '<div class="git_changes_page" markdown="1">\n' + markdown + '\n</div>'

    def remove_diff_header(self, diff):
        # Remove the diff header
        diff = re.sub(r'diff --git.*?\n@@.*?@@\n', '', diff, flags=re.DOTALL)
        return diff

    def wrap_changed_blocks(self, diff):
        # Regular expression to match blocks enclosed in triple backticks
        pattern = r'(\{\+```|\[-```|```)(.*?)(```\+\}|```-\]|```)'

        def wrap_block(match):
            # Get the entire matched block
            block = match.group(0)

            self.log.info('Block:')
            self.log.info(block)


            # Check if the block includes changes
            if re.search(r'(\{\+.*?\+\}|\[-.*?-\])', block):
                # Remove word-diff wrappers and change markers
                block = re.sub(r'\{\+(.*?)\+\}', r'\1', block)
                block = re.sub(r'\[-(.*?)-\]', r'\1', block)

                # Wrap the block in a div with a yellow background
                return '<div class="git_changes_block_changed">\n' + block + '\n</div>'
            else:
                # If the block doesn't include changes, return it unchanged
                return block

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
    


    def add_classes_to_tags(self, html, tags, classes):
        soup = BeautifulSoup(html, 'html.parser')

        # Find the heading tag and add the class
        heading_tag = soup.find(tags)
        if heading_tag:
            heading_tag['class'] = heading_tag.get('class', []) + classes

        # Return the modified HTML
        return str(soup)

    def wrap_added_headings(self, diff):
        # Process the markdown content and wrap the added headings in an HTML tag
        added_heading_pattern = re.compile(r'\{\+(\s*#+.*?)\+\}\n')

        def replacement(match):
            # Process the matched string as Markdown
            html = md.markdown(match.group(1))
            self.log.info(match.group(1))
            self.log.info(html)

            # Add the class to the heading tag
            html = self.add_classes_to_tags(html, ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], ['git_changes_added'])

            return html

        markdown = re.sub(added_heading_pattern, replacement, diff)
        return markdown
    

    def wrap_removed_headings(self, diff):
        # Process the markdown content and wrap the removed headings in an HTML tag
        removed_heading_pattern = re.compile(r'\[-(\s*#.*?)\-\]\n')

        def replacement(match):
            # Process the matched string as Markdown
            html = md.markdown(match.group(1))

            # Add the class to the heading tag
            html = self.add_classes_to_tags(html, ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'], ['git_changes_removed'])

            return html

        markdown = re.sub(removed_heading_pattern, replacement, diff)
        return markdown