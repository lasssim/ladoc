import pprint

import glob
from mkdocs.structure.files import File
import logging
import os
log = logging.getLogger(__name__)


def add_hidden_files(files, config):
  print("from on_pre_build")
  pp = pprint.PrettyPrinter(indent=4)
  hidden_files_globs = [
    ".ladoc/api_helpers/*"
  ]
  for hidden_files_glob in hidden_files_globs:
    absolute_hodden_files_glob = os.path.join(config['docs_dir'], hidden_files_glob)
    hidden_files = glob.glob(absolute_hodden_files_glob, recursive=True)
    for hidden_filename in hidden_files:
      file = File(hidden_filename.replace(config['docs_dir']+"/", ''), config['docs_dir'], config['site_dir'], config['use_directory_urls'])
      files.append(file)

  return files