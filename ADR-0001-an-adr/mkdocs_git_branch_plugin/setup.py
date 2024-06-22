from setuptools import setup, find_packages

setup(
    name='mkdocs-git-branch-plugin',
    version='0.1.0',
    description='A MkDocs plugin that adds git branch information to the site configuration',
    long_description='This MkDocs plugin captures the current Git branch during the build and makes it available to the site configuration.',
    keywords='mkdocs python markdown git',
    url='http://github.com/yourusername/mkdocs-git-branch-plugin',
    author='Simon Lasselsberger',
    author_email='simon@lasssim.com',
    license='MIT',
    python_requires='>=3.5',
    packages=find_packages(),
    entry_points={
        'mkdocs.plugins': [
            'git_branch = mkdocs_git_branch_plugin.plugin:GitBranchPlugin'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
    zip_safe=False
)
