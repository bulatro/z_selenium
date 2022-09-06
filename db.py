from sqlalchemy import create_engine, insert, table, column
from sqlalchemy.orm import sessionmaker
from config import host, port, database, user, password


engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}", echo=True)
conn = engine.connect()

itemsTab = table('tenders',
                 column('item_id'),
                 column('status'),
                 column('description'),
                 column('org'),
                 column('price'),
                 column('currency'),
                 column('start_date'),
                 column('end_date'),
                 column('short_url'),
                 column('tags'),
                 column('start_price'),
                 column('region'),
                 column('publ_date'),
                 column('domen'),
                 column('law'),
                 )

Session = sessionmaker(bind=engine)
session = Session()


def check_uniq_id(id_t):
    check = session.query(itemsTab.c.item_id).filter(itemsTab.c.item_id == id_t)
    check = session.query(check.exists()).scalar()
    return check


def insert_items(item_id, status, description, org, price, start_price, currency, start_date, end_date, short_url, tags,
                 region, publ_date, domen, law):
    ins = insert(itemsTab)
    r = conn.execute(ins,
                     item_id=item_id,
                     status=status,
                     description=description,
                     org=org,
                     price=price,
                     start_price=start_price,
                     currency = currency,
                     start_date=start_date,
                     end_date=end_date,
                     short_url=short_url,
                     tags=tags,
                     region=region,
                     publ_date=publ_date,
                     domen=domen,
                     law=law
                     )


