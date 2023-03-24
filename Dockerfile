FROM squidfunk/mkdocs-material:9.1.3

 
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

ENV PLANTUML_VERSION 1.2023.2
RUN wget https://sourceforge.net/projects/plantuml/files/plantuml.${PLANTUML_VERSION}.jar/download -O /app/plantuml.jar \
    && echo -e '#!/usr/bin/env sh \njava -Dplantuml.include.path=.:/docs/docs/.ladoc/puml_helpers/:/docs/docs/ -jar /app/plantuml.jar ${@}' >> /usr/local/bin/plantuml \
    && chmod +x /usr/local/bin/plantuml \
    && pip install plantuml-markdown \
    && echo done

RUN pip install mkdocs-macros-plugin
RUN pip install mkdocs-awesome-pages-plugin
RUN pip install mkdocs-exclude
RUN pip install pygments
RUN pip install mkdocs-video
RUN npm install yaml oas-resolver
RUN pip install mkdocs-simple-hooks
RUN pip install mkdocs-with-pdf

RUN wget https://github.com/g-provost/lightgallery-markdown/archive/master.zip -O /tmp/master.zip
RUN cd /tmp/ \
    && unzip master.zip \
    && cd lightgallery-markdown-master \ 
    && python setup.py install

COPY mkdocs /docs

CMD ["serve", "--dev-addr=0.0.0.0:1400"]
