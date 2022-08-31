from sqlalchemy import create_engine, insert, inspect, table, column, Column, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import exists



DB_SETTINGS = {
    'host': '213.189.221.184',
    'port': '5432',
    'database': 'metallsite',
    'user': 'metallsite',
    'password': 'EyPu{4L}5zhHT~VtC8x~XniK8'
}

engine = create_engine(f"postgresql+psycopg2://{DB_SETTINGS['user']}:{DB_SETTINGS['password']}@{DB_SETTINGS['host']}:"
                       f"{DB_SETTINGS['port']}/{DB_SETTINGS['database']}", echo=True)
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
                 )

Session = sessionmaker(bind=engine)
session = Session()


def check_uniq_id(id_t):
    check = session.query(itemsTab.c.item_id).filter(itemsTab.c.item_id == id_t)
    check = session.query(check.exists()).scalar()
    return check


def insert_items(item_id, status, description, org, price, start_price, currency, start_date, end_date, short_url, tags, region):
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
                     region=region
                     )


