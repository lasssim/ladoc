FROM lasssim/ladoc-base:main

COPY mkdocs /docs

CMD ["serve", "--dev-addr=0.0.0.0:1400"]
