import marimo

__generated_with = "0.11.13"
app = marimo.App(width="medium")


@app.cell
def _():
    from dataclasses import asdict

    import polars as pl

    from threads import Threads

    return Threads, asdict, pl


@app.cell
def _(Threads, asdict, pl):
    threads = Threads()
    posts, cursor_before, cursor_after = threads.get_threads(
        limit=100,
        since="2025-02-11",
    )
    print("before:", cursor_before)
    print("after:", cursor_after)
    pl.from_dicts([asdict(p) for p in posts])[["id", "timestamp", "text"]]
    return cursor_after, cursor_before, posts, threads


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
