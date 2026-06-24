from sqlalchemy import inspect
from db.session import engine

inspector = inspect(engine)

print(inspector.get_table_names())