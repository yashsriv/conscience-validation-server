drop table if exists entries;
create table entries (
	name text primary key,
	acc11 text not null,
	acc12 text not null,
	acc21 text not null,
	acc22 text not null,
	acc31 text not null,
	acc32 text not null
);

insert into entries values("marathas", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0");
insert into entries values("mauryans", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0");
insert into entries values("mughals", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0");
insert into entries values("rajputs", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0");
insert into entries values("veeras", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0");
