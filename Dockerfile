FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # PACKAGES-BEGIN
        curl \
        git \
        python3 \
        python3-venv \
        python3-pip \
        npm \
        xz-utils \
        ca-certificates \
        # PACKAGES-END
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

RUN if [ -f /usr/local/lib/hermes-agent/venv/bin/pip ]; then \
        /usr/local/lib/hermes-agent/venv/bin/pip install --break-system-packages psycopg2-binary pgvector; \
    elif [ -f /root/.hermes/hermes-agent/venv/bin/pip ]; then \
        /root/.hermes/hermes-agent/venv/bin/pip install --break-system-packages psycopg2-binary pgvector; \
    else \
        pip install --break-system-packages psycopg2-binary pgvector; \
    fi


ENV PATH="/root/.local/bin:/root/.hermes/hermes-agent/venv/bin:$PATH"
WORKDIR /app



COPY infra/hermes/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN sed -i 's/\r$//' /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 9119
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["hermes", "gateway", "run"]
