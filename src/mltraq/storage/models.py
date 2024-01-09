from sqlalchemy import BigInteger, Column, LargeBinary, String
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils.types.uuid import UUIDType

from mltraq.options import options

# Construct a base class for declarative class definitions.
Base = declarative_base()

# UUID type, to be used in model definitions. By passing binary=False, we fall back
# to the string representation of UUIDs if there's no native type  (as in SQLite).
uuid_type = UUIDType(binary=False)


class Experiment(Base):
    """Model representing the index record of an experiment in the database."""

    # TODO: use a class property to eval the value of the option.
    __tablename__ = options.get("db.experiments_tablename")
    id_experiment = Column(uuid_type, primary_key=True, default=None)
    name = Column(String, nullable=False, unique=True)
    run_count = Column(BigInteger, nullable=False, default=None)
    run_columns = Column(LargeBinary, nullable=True, default=None)
    fields = Column(LargeBinary, nullable=False, default=None)
    properties = Column(LargeBinary, nullable=False, default=None)
    pickle = Column(LargeBinary, nullable=True, default=None)
