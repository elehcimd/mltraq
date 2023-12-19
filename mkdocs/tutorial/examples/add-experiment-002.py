import mltraq
import pandas as pd
from mltraq.utils.text import wprint

session = mltraq.create_session()
experiment = session.add_experiment(
    name="test",
    description="some text",
    series=pd.Series([1, 2, 3]),
    frame=pd.DataFrame({"x": [4, 5, 6]}, index=["a", "b", "c"]),
)

experiment.persist()  # Persisting the experiment to DB
experiment = session.load(name="test")  # Loading the experiment from DB

print(f"[1] Python: experiment.fields.description = '{experiment.fields.description}'")
print(f"[2] Python: experiment.fields.series = {experiment.fields.series.tolist()}")
wprint(f'[3] SQL: {session.query("SELECT fields FROM experiments").fields.iloc[0]}')  # noqa
