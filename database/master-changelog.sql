--liquibase formatted sql

--changeset rita.linets:1 labels:init context:will ignore FKs for simplicity
--comment: create original tables
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    vector VECTOR(512) NOT NULL
);

