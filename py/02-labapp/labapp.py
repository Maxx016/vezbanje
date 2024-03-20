import os
import uuid
from datetime import datetime
import pandas as pd
import typer
from sqlalchemy import create_engine, DateTime, Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from typing_extensions import Annotated

app = typer.Typer()

dbPath = os.path.join(os.getcwd(), 'database.db')

engine = create_engine(f'sqlite:///{dbPath}')



class Base(DeclarativeBase):
    pass


class Merenje(Base):
    __tablename__ = "merenje"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, nullable=False)
    naziv_merenja: Mapped[str] = mapped_column(String(100), nullable=False)
    vreme_merenja: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    vrednost_merenja: Mapped[float] = mapped_column(Float(precision=53), nullable=False)
    vreme_unosa: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    vreme_promene: Mapped[datetime] = mapped_column(DateTime, nullable=False)


Base.metadata.create_all(engine)


@app.command()
def unos(naziv_merenja: Annotated[str, typer.Argument()],
         vreme_merenja: Annotated[datetime, typer.Argument()],
         vrednost_merenja: Annotated[float, typer.Argument()]
         ):
    with Session(engine) as session:
        formatted_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        timestamp = datetime.strptime(formatted_datetime, '%Y-%m-%d %H:%M:%S')

        novo_merenje = Merenje(
            id=str(uuid.uuid4()),
            naziv_merenja=naziv_merenja,
            vreme_merenja=vreme_merenja,
            vrednost_merenja=vrednost_merenja,
            vreme_unosa=timestamp,
            vreme_promene=timestamp
        )

        session.add(novo_merenje)
        session.commit()

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
    with Session(engine) as session:
        query = session.query(Merenje)

        if id:
            query = query.filter(Merenje.id == id)
        if naziv:
            query = query.filter(Merenje.naziv_merenja == naziv)
        if vreme:
            query = query.filter(Merenje.vreme_merenja == vreme)
        if vrednost:
            query = query.filter(Merenje.vrednost_merenja == vrednost)
        if vreme_unosa:
            query = query.filter(Merenje.vreme_unosa == vreme_unosa)

        query = query.offset(offset).limit(limit)

        df = pd.read_sql(query.statement, session.bind)

        if not df.empty:
            print(df)


@app.command()
def brisanje(id: Annotated[uuid.UUID, typer.Argument(help="id merenja za brisanje")]):
    with Session(engine) as session:
        to_delete = session.query(Merenje).filter(Merenje.id == (str(id))).first()

        if to_delete:
            session.delete(to_delete)
            session.commit()

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

    with Session(engine) as session:
        to_update = session.query(Merenje).filter(Merenje.id == str(id)).first()

        if to_update:
            if naziv:
                to_update.naziv_merenja = naziv
            if vreme:
                to_update.vreme_merenja = vreme
            if vrednost:
                to_update.vrednost_merenja = vrednost

            session.commit()
            print(f"Uspesno izmenjeno merenje id {id}")

        else:
            print(f"Merenje nije pronadjeno! id: {id}")


if __name__ == "__main__":
    app()
