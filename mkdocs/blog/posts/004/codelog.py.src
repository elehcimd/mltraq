from mltraq import create_experiment, options
from mltraq.steps.init_fields import init_fields

with options().ctx({"codelog.disable": False}):
    e = create_experiment().execute(init_fields(a=1))


for idx, codelog in enumerate(e.runs.first().fields.codelog):
    print(
        f"Step {idx}: {codelog.pathname}:{codelog.pathname_lineno} "
        f"@ {codelog.name}(*{codelog.args}, **{codelog.kwargs})"
    )
    print(f"\n--\n{codelog.code}\n--\n")
