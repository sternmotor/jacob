PostgreSQL Administration
=========================


psql -U postgres -c 'SELECT usename,client_addr,backend_start,now() - pg_stat_activity.query_start AS duration,state FROM pg_stat_activity ORDER BY backend_start'

Install module
--------------



