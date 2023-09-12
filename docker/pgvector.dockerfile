FROM postgres:latest

# Install dependencies for vector
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        postgresql-server-dev-all \
        git \
        curl

# Clone and build the vector extension
RUN git clone https://github.com/ankane/pgvector.git \
    && cd pgvector \
    && make && make install

EXPOSE 5432
