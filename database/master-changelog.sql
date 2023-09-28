--liquibase formatted sql

--changeset rita.linets:1 labels:init context:will ignore FKs for simplicity
--comment: create original tables
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    vector VECTOR(768) NOT NULL
);

CREATE TABLE tbl_chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL, 
    room_id INTEGER NOT NULL,
    ordinal_position INTEGER NOT NULL,
    message jsonb NOT NULL
);

