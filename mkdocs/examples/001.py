from mltraq import create_experiment


def f1(run):
    """
    Store inputs as fields and compute AB
    """
    run.fields.A = run.params.A
    run.fields.B = run.params.B
    run.fields.C = run.config.C
    run.fields.AB = run.fields.A + run.fields.B


def f2(run):
    """
    Compute ABC
    """
    run.fields.ABC = run.fields.AB + run.fields.C


def f3(run):
    """
    Compute ABCD
    """
    run.fields.ABCD = run.fields.ABC + run.config.D


print(
    create_experiment("example")
    .add_runs(A=[1, 2], B=[3, 4])  # Parameters grid
    .execute([f1, f2], config={"C": 5})  # Execute steps
    .persist()  # Persistence to database
    .reload()  # Reload experiment from database
    .execute(f3, config={"D": 6})  # Continue execution
    .persist(if_exists="replace")  # Persist to database
    .db.query("SELECT * FROM experiment_example")  # SQL query
)
