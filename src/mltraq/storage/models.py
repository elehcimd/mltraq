from sqlalchemy import Column, LargeBinary, String, Uuid
from sqlalchemy.orm import DeclarativeBase

from mltraq.opts import options


# Define a base class for declarative class definitions.
class Base(DeclarativeBase):
    pass


# Using the recently introduced UUID type:
# https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Uuid


class Experiment(Base):
    """
    Model representing the index record of an experiment in the database:
    - id_experiment: random UUID
    - name: short 6-len alphanum hash of id_experiemnt by default
    - meta: metadata about the serialized experiment
    - fields: experiment state fields
    - unsafe_pickle: pickled (unsafe) Experiment object
    """

    # TODO: Use a class property to eval the value of the option.
    # Currently, changing the value of the option does not result
    # in an updated value for __tablename__.
    __tablename__ = options().get("database.experiments_tablename")
    id_experiment = Column(Uuid, primary_key=True, default=None)
    name = Column(String, nullable=False, unique=True)
    meta = Column(LargeBinary, nullable=True, default=None)
    fields = Column(LargeBinary, nullable=False, default=None)
    unsafe_pickle = Column(LargeBinary, nullable=True, default=None)
