FROM squidfunk/mkdocs-material:9.0.15

 
RUN mkdir -p /app


RUN apk add --no-cache \
    graphviz \
    openjdk8-jre \
    ttf-droid \
    #ttf-droid-nonlatin \
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
RUN pip install mkdocs-plugin-inline-svg
RUN pip install pygments
RUN pip install mkdocs-video
#RUN pip install git+https://github.com/lasssim/mkdocs.git@master
#COPY tmp/mkdocs /tmp/mkdocs
#RUN pip install file:///tmp/mkdocs

RUN npm install yaml oas-resolver

RUN wget https://github.com/g-provost/lightgallery-markdown/archive/master.zip -O /tmp/master.zip
RUN cd /tmp/ \
    && unzip master.zip \
    && cd lightgallery-markdown-master \ 
    && python setup.py install
RUN pip install mkdocs-simple-hooks
RUN pip install mkdocs-with-pdf


COPY mkdocs /docs

CMD ["serve", "--dev-addr=0.0.0.0:1400", "-v"]