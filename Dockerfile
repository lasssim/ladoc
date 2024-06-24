FROM squidfunk/mkdocs-material:9.5

 
RUN mkdir -p /app

RUN apk add --no-cache \
    graphviz \
    openjdk8-jre \
    ttf-droid \
    nghttp2-dev \
    nodejs \
    npm \
    build-base

RUN pip install --upgrade pip

ENV PLANTUML_VERSION 1.2024.5
RUN wget https://github.com/plantuml/plantuml/releases/download/v${PLANTUML_VERSION}/plantuml-${PLANTUML_VERSION}.jar -O /app/plantuml.jar \
    && echo -e '#!/usr/bin/env sh \njava -Dplantuml.include.path=.:/docs/docs/.ladoc/puml_helpers/:/docs/docs/ -jar /app/plantuml.jar ${@}' >> /usr/local/bin/plantuml \
    && chmod +x /usr/local/bin/plantuml \
    && pip install plantuml-markdown \
    && echo done

RUN MAKEFLAGS="-j$(nproc)" pip install mkdocs-macros-plugin \
    mkdocs-awesome-pages-plugin \
    mkdocs-exclude \
    pygments \
    mkdocs-video \
    mkdocs-simple-hooks \
    mkdocs-with-pdf \
    mkdocs-glightbox \
    pymdown-extensions \
    mike \
    && npm install -g yaml oas-resolver

RUN apk del build-base \
    && rm -rf /var/cache/apk/* \
    && rm -rf /tmp/*

COPY mkdocs /docs

CMD ["serve", "--dev-addr=0.0.0.0:1400"]
