import os

def define_env(env):
    """
    This is the hook for defining variables, macros and filters

    - variables: the dictionary that contains the environment variables
    - macro: a decorator function, to declare a macro.
    """

   # create a jinja2 filter
    @env.macro
    def api_spec_link(yaml_filenamepath, label="API"):
      return "[" + label + "](/redoc.html?url=/" + yaml_filenamepath + ")"
    
    @env.macro
    def generate_subnav(current_page):
        subnav = []
        path = os.path.dirname(current_page.file.src_path)
        for root, dirs, files in os.walk(path):
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * (level)
            subnav.append(f"{indent}- [{os.path.basename(root)}]({root}/index.md)")
            sub_indent = ' ' * 4 * (level + 1)
            for f in files:
                if f.endswith('.md') and f != 'index.md':
                    subnav.append(f"{sub_indent}- [{f[:-3]}]({root}/{f})")
        return '\n'.join(subnav)   