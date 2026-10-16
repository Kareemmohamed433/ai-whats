import os
import sys

# Must set before SQLAlchemy is imported
os.environ["DISABLE_SQLALCHEMY_CEXT"] = "1"

# Also try deleting/bypassing _collections_cy if blocked on Windows
try:
    import sqlalchemy.util._collections
    sqlalchemy.util._collections.HAVE_CYTHON = False
except Exception:
    pass
