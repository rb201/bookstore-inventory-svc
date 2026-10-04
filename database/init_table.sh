#!/bin/bash

docker exec -it inv-pg psql -U ${pguser} -d inventory < schema.sql