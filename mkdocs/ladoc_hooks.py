import pprint

import glob
from mkdocs.structure.files import File
import logging
import os
from datetime import datetime
log = logging.getLogger(__name__)


def add_hidden_files(files, config):
  #print("------ from on_pre_build")
  #pp = pprint.PrettyPrinter(indent=4)
  hidden_files_globs = [
    ".ladoc/api_helpers/**",
    ".ladoc/assets/**"
  ]
  #pp.pprint(config)
  for hidden_files_glob in hidden_files_globs:
    absolute_hidden_files_glob = os.path.join(config['docs_dir'], hidden_files_glob)
    hidden_files = glob.glob(absolute_hidden_files_glob, recursive=True)
    #pp.pprint(hidden_files)
    for hidden_filename in hidden_files:
      #pp.pprint(os.path.exists(hidden_filename))
      #pp.pprint(hidden_filename)
      if not os.path.exists(hidden_filename):
        continue
      if os.path.isdir(hidden_filename):
        continue
      file = File(hidden_filename.replace(config['docs_dir']+"/", ''), config['docs_dir'], config['site_dir'], config['use_directory_urls'])
      #pp.pprint(file)
      files.append(file)
  #pp.pprint(files)
  return files

def set_build_time_env_var(*args, **kwargs):
  #print("------ from on_post_build")
  os.environ['LADOC_BUILD_DATE'] = datetime.now().strftime("%Y-%m-%d")
  #pp.pprint(os.environ['LADOC_BUILD_TIME'])