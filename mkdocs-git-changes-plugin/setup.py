from setuptools import setup, find_packages

setup(
    name='mkdocs-git-changes-plugin',
    version='0.1.0',
    description='A MkDocs plugin that adds git changes information to the site',
    long_description='This MkDocs plugin captures the current Git changes during the build and displays it on the site.',
    keywords='mkdocs python markdown git',
    url='http://github.com/yourusername/mkdocs-git-changes-plugin',
    author='Simon Lasselsberger',
    author_email='simon@lasssim.com',
    license='MIT',
    python_requires='>=3.5',
    packages=find_packages(),
    entry_points={
        'mkdocs.plugins': [
            'git-changes = plugin.main:GitChangesPlugin'
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