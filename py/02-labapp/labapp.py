import typer
from sqlalchemy import create_engine, text
import os
import uuid
from datetime import datetime
from typing_extensions import Annotated
import pandas as pd

app = typer.Typer()

dbPath = os.path.join(os.getcwd(), 'database.db')

engine = create_engine(f'sqlite:///{dbPath}')

conn = engine.connect()

conn.execute(text("""
    CREATE TABLE IF NOT EXISTS merenje (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    naziv_merenja VARCHAR(100) NOT NULL,
    vreme_merenja DATETIME NOT NULL,
    vrednost_merenja DOUBLE NOT NULL,
    vreme_unosa DATETIME NOT NULL,
    vreme_promene DATETIME NOT NULL
    )
"""))


@app.command()
def unos(naziv_merenja: Annotated[str, typer.Argument()],
    vreme_merenja: Annotated[datetime, typer.Argument()],
    vrednost_merenja: Annotated[float, typer.Argument()]
):
    conn.execute(text(f"""
        INSERT INTO merenje (
            id,
            naziv_merenja,
            vreme_merenja,
            vrednost_merenja,
            vreme_unosa,
            vreme_promene)
        VALUES (
            '{uuid.uuid4()}',
            '{naziv_merenja}',
            '{vreme_merenja}',
            {vrednost_merenja},
            '{str(datetime.now().replace(microsecond=0))}',
            '{str(datetime.now().replace(microsecond=0))}'
        )
    """))
    conn.commit()
    print("Uspesno ste uneli merenje.")


@app.command()
def pregled(
    id: Annotated[uuid.UUID, typer.Option(help="uuid4 merenja")] = None,
    naziv: Annotated[str, typer.Option(help="naziv merenja")] = "",
    vreme: Annotated[datetime, typer.Option(help="vreme merenja")] = None,
    vrednost: Annotated[float, typer.Option(help="vrednost merenja")] = False,
    vreme_unosa: Annotated[datetime, typer.Option(help="vreme unosa merenja")] = None,
    limit: Annotated[int, typer.Option(help="limit prikaza rezultata")] = 10,
    offset: Annotated[int, typer.Option(help="redni broj reda rezultata od kojeg pocinje listanje rezultata")] = 0
):
    options = [
        ("id", id),
        ("naziv_merenja", naziv),
        ("vreme_merenja", vreme),
        ("vrednost_merenja", vrednost),
        ("vreme_unosa", vreme_unosa),
    ]

    query = "SELECT * FROM MERENJE"
    queryString = ""

    for k, v in options:
        if v:
            if not queryString:
                queryString = f" WHERE {k} = '{v}'"
            else:
                queryString += f" AND {k} = '{v}'"

    query += queryString
    query += f" LIMIT {offset}, {limit}"
    result = conn.execute(text(query))
    df = pd.DataFrame(result)
    if not df.empty:
        print(df)


@app.command()
def brisanje(id: Annotated[uuid.UUID, typer.Argument(help="id merenja za brisanje")]):
    if conn.execute(text(f"DELETE FROM merenje WHERE id = '{id}'")).rowcount > 0:
        conn.commit()
        print(f"Uspesno obrisano merenje id {id}!")
    else:
        print(f"Merenje nije pronadjeno! id: {id}")


@app.command()
def promena(
    id: Annotated[uuid.UUID, typer.Argument(help="id merenja za promenu")] = None,
    naziv: Annotated[str, typer.Option(help="novi naziv merenja")] = "",
    vreme: Annotated[datetime, typer.Option(help="novo vreme merenja")] = None,
    vrednost: Annotated[float, typer.Option(help="nova vrednost merenja")] = False
):
    if not any([naziv, vreme, vrednost]):
        print("Morate izabrati neku od opcija! (brisanje --help)")
        return

    options = [
      ("naziv_merenja", naziv),
      ("vreme_merenja", vreme),
      ("vrednost_merenja", vrednost)
    ]

    queryString = ""
    for k, v in options:
        if v:
            if not queryString:
                queryString += f" {k} = '{v}'"
            else:
                queryString += f", {k} = '{v}'"

    query = "UPDATE merenje SET"
    query += queryString
    query += f" WHERE id = '{id}'"

    if conn.execute(text(query)).rowcount > 0:
        conn.commit()
        print(f"Uspesno izmenjeno merenje id {id}")
    else:
        print(f"Merenje nije pronadjeno! id: {id}")


if __name__ == "__main__":
    app()
