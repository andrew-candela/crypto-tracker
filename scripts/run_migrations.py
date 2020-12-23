from service.lib import pg


SQL = "scripts/create_tables.sql"


def run_sql_scripts():
    postgres = pg.PG()
    with postgres.create_connection() as conn:
        postgres.execute_sql_file(SQL, conn)


if __name__ == "__main__":
    run_sql_scripts()
