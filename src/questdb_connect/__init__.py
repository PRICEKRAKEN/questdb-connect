#
#     ___                  _   ____  ____
#    / _ \ _   _  ___  ___| |_|  _ \| __ )
#   | | | | | | |/ _ \/ __| __| | | |  _ \
#   | |_| | |_| |  __/\__ \ |_| |_| | |_) |
#    \__\_\\__,_|\___||___/\__|____/|____/
#
#  Copyright (c) 2014-2019 Appsicle
#  Copyright (c) 2019-2023 QuestDB
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import os
import re
import time

import psycopg2

# QuestDB timestamps: https://questdb.io/docs/guides/working-with-timestamps-timezones/
# The native timestamp format used by QuestDB is a Unix timestamp in microsecond resolution.
# Although timestamps in nanoseconds will be parsed, the output will be truncated to
# microseconds. QuestDB does not store time zone information alongside timestamp values
# and therefore it should be assumed that all timestamps are in UTC.
os.environ["TZ"] = "UTC"
time.tzset()

# ===== DBAPI =====
# https://peps.python.org/pep-0249/

apilevel = "2.0"
threadsafety = 2
paramstyle = "pyformat"
public_schema_filter = re.compile(
    r"(')?(public(?(1)\1|)\.)", re.IGNORECASE | re.MULTILINE
)


def remove_public_schema(query):
    if query and isinstance(query, str) and "public" in query:
        return re.sub(public_schema_filter, "", query)
    return query


class Error(Exception):
    pass


class Cursor(psycopg2.extensions.cursor):
    def execute(self, query, vars=None):
        """execute(query, vars=None) -- Execute query with bound vars."""
        return super().execute(remove_public_schema(query), vars)


def cursor_factory(*args, **kwargs):
    return Cursor(*args, **kwargs)


def get_function_names():
    return __func_names


def get_keywords():
    return __keywords


def connect(**kwargs):
    host = kwargs.get("host") or "127.0.0.1"
    port = kwargs.get("port") or 8812
    user = kwargs.get("username") or "admin"
    password = kwargs.get("password") or "quest"
    database = kwargs.get("database") or "main"
    conn = psycopg2.connect(
        cursor_factory=cursor_factory,
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
    __initialize_list(
        conn, "SELECT name FROM functions()", __func_names, __default_func_names
    )
    __initialize_list(
        conn, "SELECT keyword FROM keywords()", __keywords, __default_keywords
    )
    return conn


def __initialize_list(conn, sql_stmt, target_list, default_target_list):
    if not target_list:
        try:
            with conn.cursor() as functions_cur:
                functions_cur.execute(sql_stmt)
                for func_row in functions_cur.fetchall():
                    target_list.append(func_row[0])
        except psycopg2.DatabaseError:
            target_list.extend(default_target_list)


__func_names = []
__default_func_names = [
    "abs",
    "acos",
    "all_tables",
    "and",
    "asin",
    "atan",
    "atan2",
    "avg",
    "base64",
    "between",
    "build",
    "case",
    "cast",
    "ceil",
    "ceiling",
    "coalesce",
    "concat",
    "cos",
    "cot",
    "count",
    "count_distinct",
    "current_database",
    "current_schema",
    "current_schemas",
    "current_user",
    "date_trunc",
    "dateadd",
    "datediff",
    "day",
    "day_of_week",
    "day_of_week_sunday_first",
    "days_in_month",
    "degrees",
    "dump_memory_usage",
    "dump_thread_stacks",
    "extract",
    "first",
    "floor",
    "flush_query_cache",
    "format_type",
    "haversine_dist_deg",
    "hour",
    "ilike",
    "information_schema._pg_expandarray",
    "isOrdered",
    "is_leap_year",
    "ksum",
    "last",
    "left",
    "length",
    "like",
    "list",
    "log",
    "long_sequence",
    "lower",
    "lpad",
    "ltrim",
    "make_geohash",
    "max",
    "memory_metrics",
    "micros",
    "millis",
    "min",
    "minute",
    "month",
    "not",
    "now",
    "nsum",
    "nullif",
    "pg_advisory_unlock_all",
    "pg_attrdef",
    "pg_attribute",
    "pg_catalog.age",
    "pg_catalog.current_database",
    "pg_catalog.current_schema",
    "pg_catalog.current_schemas",
    "pg_catalog.pg_attrdef",
    "pg_catalog.pg_attribute",
    "pg_catalog.pg_class",
    "pg_catalog.pg_database",
    "pg_catalog.pg_description",
    "pg_catalog.pg_get_expr",
    "pg_catalog.pg_get_keywords",
    "pg_catalog.pg_get_partkeydef",
    "pg_catalog.pg_get_userbyid",
    "pg_catalog.pg_index",
    "pg_catalog.pg_inherits",
    "pg_catalog.pg_is_in_recovery",
    "pg_catalog.pg_locks",
    "pg_catalog.pg_namespace",
    "pg_catalog.pg_roles",
    "pg_catalog.pg_shdescription",
    "pg_catalog.pg_table_is_visible",
    "pg_catalog.pg_type",
    "pg_catalog.txid_current",
    "pg_catalog.version",
    "pg_class",
    "pg_database",
    "pg_description",
    "pg_get_expr",
    "pg_get_keywords",
    "pg_get_partkeydef",
    "pg_index",
    "pg_inherits",
    "pg_is_in_recovery",
    "pg_locks",
    "pg_namespace",
    "pg_postmaster_start_time",
    "pg_proc",
    "pg_range",
    "pg_roles",
    "pg_type",
    "position",
    "power",
    "radians",
    "reader_pool",
    "regexp_replace",
    "replace",
    "right",
    "rnd_bin",
    "rnd_boolean",
    "rnd_byte",
    "rnd_char",
    "rnd_date",
    "rnd_double",
    "rnd_float",
    "rnd_geohash",
    "rnd_int",
    "rnd_log",
    "rnd_long",
    "rnd_long256",
    "rnd_short",
    "rnd_str",
    "rnd_symbol",
    "rnd_timestamp",
    "rnd_uuid4",
    "round",
    "round_down",
    "round_half_even",
    "round_up",
    "row_number",
    "rpad",
    "rtrim",
    "second",
    "session_user",
    "simulate_crash",
    "sin",
    "size_pretty",
    "split_part",
    "sqrt",
    "starts_with",
    "stddev_samp",
    "string_agg",
    "strpos",
    "substring",
    "sum",
    "switch",
    "sysdate",
    "systimestamp",
    "table_columns",
    "table_partitions",
    "table_writer_metrics",
    "tables",
    "tan",
    "timestamp_ceil",
    "timestamp_floor",
    "timestamp_sequence",
    "timestamp_shuffle",
    "to_char",
    "to_date",
    "to_long128",
    "to_lowercase",
    "to_pg_date",
    "to_str",
    "to_timestamp",
    "to_timezone",
    "to_uppercase",
    "to_utc",
    "touch",
    "trim",
    "txid_current",
    "typeOf",
    "upper",
    "version",
    "wal_tables",
    "week_of_year",
    "year",
]
__keywords = []
__default_keywords = [
    "add",
    "all",
    "alter",
    "and",
    "as",
    "asc",
    "asof",
    "backup",
    "between",
    "by",
    "cache",
    "capacity",
    "case",
    "cast",
    "column",
    "columns",
    "copy",
    "create",
    "cross",
    "database",
    "default",
    "delete",
    "desc",
    "distinct",
    "drop",
    "else",
    "end",
    "except",
    "exists",
    "fill",
    "foreign",
    "from",
    "grant",
    "group",
    "header",
    "if",
    "in",
    "index",
    "inner",
    "insert",
    "intersect",
    "into",
    "isolation",
    "join",
    "key",
    "latest",
    "limit",
    "lock",
    "lt",
    "nan",
    "natural",
    "nocache",
    "none",
    "not",
    "null",
    "on",
    "only",
    "or",
    "order",
    "outer",
    "over",
    "partition",
    "primary",
    "references",
    "rename",
    "repair",
    "right",
    "sample",
    "select",
    "show",
    "splice",
    "system",
    "table",
    "tables",
    "then",
    "to",
    "transaction",
    "truncate",
    "type",
    "union",
    "unlock",
    "update",
    "values",
    "when",
    "where",
    "with",
    "writer",
]
