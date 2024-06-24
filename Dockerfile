FROM lasssim/ladoc-base:latest

COPY mkdocs /docs

CMD ["serve", "--dev-addr=0.0.0.0:1400"]
