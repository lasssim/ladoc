import logging
from git import Repo
from mkdocs.config import config_options, Config
from mkdocs.plugins import BasePlugin
import re
import os
import markdown as md
from bs4 import BeautifulSoup
import json

class GitChangesPlugin(BasePlugin):

    config_scheme = (
        ('reference_branch', config_options.Type(str, default='main')),
        ('doc_path', config_options.Type(str, default='.')),
        ('enabled_in_dev', config_options.Type(bool, default=False))
    )

    def __init__(self):
        self.log = logging.getLogger(f"mkdocs.plugins.{__name__}")

    def on_config(self, config):
        self.reference_branch = self.config['reference_branch']
        self.doc_path = self.config['doc_path'].rstrip('/')
        self.enabled_in_dev = self.config['enabled_in_dev'] if 'enabled_in_dev' in self.config else False

        self.repo = Repo(self.doc_path)
        self.repo.git.config('--global', '--add', 'safe.directory', self.doc_path)

#        print(f"Repo directory: {self.repo.working_tree_dir}")
#        print(f"Is the repo bare? {self.repo.bare}")
#
#        print("Repo status:")
#        print(self.repo.git.status())
#
#        print("Branches:")
#        for branch in self.repo.branches:
#            print(f"- {branch}")
        self.log.info("Reseting changed pages")
        self.reset_changed_pages()
        

        return config
    
    def on_startup(self, command, dirty):
        self.is_build = command != 'serve'

    def _enabled(self, config):
        return (self.enabled_in_dev and not self.is_build) or self.is_build
         
    def on_page_markdown(self, markdown, page, config, files):
        if not self._enabled(config):
            return markdown

        diff = self.diff(page)
        if not diff.strip():
            return markdown        
        
        self.add_changed_page(page)

        markdown = self.remove_diff_header(diff)
        markdown = self.remove_yaml_header(markdown)

        markdown = self.wrap_page(markdown)

        markdown = self.wrap_changed_blocks(markdown)
        markdown = self.wrap_changed_tables(markdown)

        markdown = self.wrap_added_headings(markdown)
        markdown = self.wrap_removed_headings(markdown)

        markdown = self.wrap_added_bullets(markdown)
        markdown = self.wrap_removed_bullets(markdown)

        markdown = self.wrap_added_numbers(markdown)
        markdown = self.wrap_removed_numbers(markdown)

        markdown = self.wrap_added_quotes(markdown)
        markdown = self.wrap_removed_quotes(markdown)

        markdown = self.wrap_added_words(markdown)
        markdown = self.wrap_removed_words(markdown)


#        self.log.info(markdown)
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

#            self.log.info('Block:')
#            self.log.info(block)


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
    
    
    
    def wrap_added_bullets(self, diff):
        # Define the regular expression pattern
        pattern = re.compile(r'(\{\+(\s*[\*\-]\s*)(.*?)\+\})')
        markdown = re.sub(pattern, r'\2<span class="git_changes_added" markdown="1">\3</span>', diff)
        return markdown

    def wrap_removed_bullets(self, diff):
        pattern = re.compile(r'(\[-(\s*[\*\-]\s*)(.*?)-\])')
        markdown = re.sub(pattern, r'\2<span class="git_changes_removed" markdown="1">\3</span>', diff)
        return markdown


    def wrap_added_numbers(self, diff):
        pattern = re.compile(r'(\{\+(\s*\d+\.\s*)(.*?)\+\})')
        markdown = re.sub(pattern, r'\2<span class="git_changes_added" markdown="1">\3</span>', diff)
        return markdown

    def wrap_removed_numbers(self, diff):
        pattern = re.compile(r'(\[-(\s*\d+\.\s*)(.*?)-\])')
        markdown = re.sub(pattern, r'\2<span class="git_changes_removed" markdown="1">\3</span>', diff)
        return markdown


    def wrap_added_quotes(self, diff):
        pattern = re.compile(r'(\{\+(\s*>\s*)(.*?)\+\})')
        markdown = re.sub(pattern, r'\2<span class="git_changes_added" markdown="1">\3</span>', diff)
        return markdown
    
    def wrap_removed_quotes(self, diff):
        pattern = re.compile(r'(\[-(\s*>\s*)(.*?)-\])')
        markdown = re.sub(pattern, r'\2<span class="git_changes_removed" markdown="1">\3</span>', diff)
        return markdown

    def wrap_changed_tables(self, diff):
        #find tables (each line starting with {+, [- or | 
        # capture until there is a line that does not start with {+, [- or |

        # Regular expression to match tables
        pattern = r'(\{\+\s*\|.*?\n|\[-\s*\|.*?\n|\s*\|.*?\n)+'

        def wrap_table(match):
            # Get the entire matched table
            table = match.group(0)

            # Check if the table includes changes
            if re.search(r'(\{\+.*?\+\}|\[-.*?-\])', table):
                # Remove word-diff wrappers and change markers
                table = re.sub(r'\{\+(.*?)\+\}', r'\1', table)
                table = re.sub(r'\[-(.*?)-\]', r'\1', table)

                # Wrap the table in a div with a yellow background
                return '<div class="git_changes_table_changed" markdown="1">\n' + table + '\n</div>'
            else:
                # If the table doesn't include changes, return it unchanged
                return table
            
        # Apply the regular expression and the wrap_table function to the diff
        diff = re.sub(pattern, wrap_table, diff, flags=re.DOTALL)

        return diff


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
#            self.log.info(match.group(1))
#            self.log.info(html)

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
#        print("Repo status")
#        self.log.info(self.repo.git.status('-v'))
        try:
            ret = self.repo.git.rev_parse('--verify', '-v', self.reference_branch)
#            print("Repo verify")
#            self.log.info(ret)
        except:
            ret = self.repo.git.fetch('origin', '-v', self.reference_branch)
#            print("Fetch reference branch")
#            self.log.info(ret)
#            print("Repo verify")
#            self.log.info(self.repo.git.rev_parse('--verify', '-v',
#            self.reference_branch))

    def reset_changed_pages(self):
        filename = 'docs/changed_pages.json'
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
        if os.path.exists(filename):
            os.remove(filename) 

    def add_changed_page(self, page):
        self.log.info("Adding changed page: " + page.file.src_path)
        filename = 'docs/changed_pages.json'
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
        try:
            with open(filename, 'r') as file:
                changed_pages = json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            changed_pages = {}

        changed_pages[page.file.src_path] = page.url

        with open(filename, 'w') as file:
            json.dump(changed_pages, file)