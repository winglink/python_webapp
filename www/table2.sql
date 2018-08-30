drop database if exists webpython;
create database webpython;


create user 'wing'@'localhost' identified by 'wing';
grant select,insert,update,delete on webpython.* to 'wing'@'localhost';

use webpython;

create table User (
     `id`   varchar(50)   not null,
     `email`   varchar(50)   not null,
     `passwd`   varchar(50)   not null,
     `admin`   boolean   not null,
     `name`   varchar(50)   not null,
     `image`   varchar(500)   not null,
     `created_at`   real   not null,
      unique key   `idx_email` (`email`),
      key   `idx_created_at` (`created_at`),
      primary key (`id`)
) engine=innodb default charset=utf8; 


 create table Blog (
     `id`   varchar(50)   not null,
     `user_id`   varchar(50)   not null,
     `user_name`   varchar(50)   not null,
     `user_image`   varchar(500)   not null,
     `name`   varchar(50)   not null,
     `summary`   varchar(50)   not null,
     `content`   text   not null,
     `created_at`   real   not null,
       key `idx_created_at`  (`created_at`),  
      primary key (`id`)
) engine=innodb default charset=utf8;


 create table Comment (
     `id`   varchar(50)   not null,
     `blog_id`   varchar(50)   not null,
     `user_id`   varchar(50)   not null,
     `user_name`   varchar(50)   not null,
     `user_image`   varchar(500)   not null,
     `content`   text   not null,
     `created_at`   real   not null,
     key `idx_created_at`  (`created_at`),
      primary key (`id`)
) engine=innodb default charset=utf8;


 