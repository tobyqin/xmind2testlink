drop table if exists records;

create table records (
  id integer primary key autoincrement,
  title text not null,
  note text
);