drop database if exists bot_db;
create database bot_db;

use bot_db;
create table user_info (
   user_id VARCHAR(40),
   username VARCHAR(40),
   link_karma INTEGER,
   comment_karma INTEGER,
   created VARCHAR(40),
   verified VARCHAR(40),
   submissions INTEGER,
   comments INTEGER,
	PRIMARY KEY (user_id)
);