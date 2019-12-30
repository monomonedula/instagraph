CREATE SCHEMA IF NOT EXISTS social;

CREATE TABLE IF NOT EXISTS social.users
(
    id bigint NOT NULL,
    username character varying(255) COLLATE pg_catalog."default",
    posts_number integer,
    name character varying(255) COLLATE pg_catalog."default",
    bio text COLLATE pg_catalog."default",
    website character varying(255) COLLATE pg_catalog."default",
    account_type character varying COLLATE pg_catalog."default",
    nfollowers integer,
    nfollows integer,
    tags character varying[] DEFAULT '{}'::character varying[],
    CONSTRAINT users_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;



CREATE TABLE IF NOT EXISTS social.posts
(
    user_id bigint NOT NULL,
    id bigint NOT NULL,
    caption text COLLATE pg_catalog."default",
    taken_at timestamp,
    nlikes integer,
    location bigint,
    CONSTRAINT posts_pkey PRIMARY KEY (user_id, id),
    CONSTRAINT posts_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES social.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE TABLE IF NOT EXISTS social.posts_media
(
    posts_user_id bigint NOT NULL,
    posts_post_id bigint NOT NULL,
    id character varying(100) NOT NULL,
    file_path character varying(255) COLLATE pg_catalog."default",
    file_type character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT posts_media_pkey PRIMARY KEY (id, posts_post_id, posts_user_id),
    CONSTRAINT posts_media_posts_user_id_fkey FOREIGN KEY (posts_post_id, posts_user_id)
        REFERENCES social.posts (id, user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE TABLE IF NOT EXISTS social.likes
(
    user_id bigint NOT NULL,
    post_id bigint NOT NULL,
    post_user_id bigint NOT NULL,
    CONSTRAINT likes_pkey PRIMARY KEY (user_id, post_id, post_user_id),
    CONSTRAINT likes_post_id_fkey FOREIGN KEY (post_id, post_user_id)
        REFERENCES social.posts (id, user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT likes_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES social.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;



CREATE TABLE IF NOT EXISTS social.post_user_tags
(
    user_id bigint NOT NULL,
    post_id bigint NOT NULL,
    post_user_id bigint NOT NULL,
    CONSTRAINT post_user_tags_pkey PRIMARY KEY (user_id, post_id, post_user_id),
    CONSTRAINT post_user_tags_post_id_fkey FOREIGN KEY (post_id, post_user_id)
        REFERENCES social.posts (id, user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT post_user_tags_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES social.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE TABLE IF NOT EXISTS social.connections
(
    follower bigint NOT NULL,
    followed bigint NOT NULL,
    CONSTRAINT connections_pkey PRIMARY KEY (follower, followed),
    CONSTRAINT connections_followed_fkey FOREIGN KEY (followed)
        REFERENCES social.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT connections_follower_fkey FOREIGN KEY (follower)
        REFERENCES social.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;



CREATE TABLE IF NOT EXISTS social.connections_timeline
(
    follower bigint NOT NULL,
    followed bigint NOT NULL,
    observed date NOT NULL,
    ended date,
    CONSTRAINT connections_timeline_pkey PRIMARY KEY (follower, followed, observed),
    CONSTRAINT connections_followed_fkey FOREIGN KEY (followed)
        REFERENCES social.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT connections_follower_fkey FOREIGN KEY (follower)
        REFERENCES social.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE TABLE IF NOT EXISTS social.follow_schedule
(
    follower bigint NOT NULL,
    followed bigint NOT NULL,
    scheduled date NOT NULL,
    done date,
    priority integer,
    tags character varying[] DEFAULT '{}'::character varying[],
    CONSTRAINT follow_schedule_pkey PRIMARY KEY (follower, followed)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE TABLE IF NOT EXISTS social.unfollow_schedule
(
    follower bigint NOT NULL,
    unfollowed bigint NOT NULL,
    scheduled date NOT NULL,
    done date,
    priority integer,
    tags character varying[] DEFAULT '{}'::character varying[],
    CONSTRAINT unfollow_schedule_pkey PRIMARY KEY (follower, unfollowed)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE TABLE IF NOT EXISTS social.likes_timeline
(
    user_id bigint NOT NULL,
    post_id bigint  NOT NULL,
    post_user_id bigint NOT NULL,
    CONSTRAINT likes_timeline_pkey PRIMARY KEY (user_id, post_id, post_user_id),
    CONSTRAINT likes_post_id_fkey FOREIGN KEY (post_id, post_user_id)
        REFERENCES social.posts (id, user_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION,
    CONSTRAINT likes_user_id_fkey FOREIGN KEY (user_id)
        REFERENCES social.users (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE NO ACTION
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE TABLE IF NOT EXISTS social.users_timeline
(
    id bigint NOT NULL,
    username character varying(255) COLLATE pg_catalog."default",
    posts_number integer,
    name character varying(255) COLLATE pg_catalog."default",
    bio text COLLATE pg_catalog."default",
    website character varying(255) COLLATE pg_catalog."default",
    account_type character varying COLLATE pg_catalog."default",
    nfollowers integer,
    nfollows integer,
    tags character varying[] DEFAULT '{}'::character varying[],
    observed date,
    CONSTRAINT users_timeline_pkey PRIMARY KEY (id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;


CREATE TABLE IF NOT EXISTS social.actions
(
    user_id bigint,
    date_taken date,
    action_type character varying(255)
)
WITH (
    OIDS = FALSE
);


CREATE TABLE IF NOT EXISTS social.locations
(
    location_id bigint,
    name character varying(255),
    lat double precision,
    lng double precision
);
