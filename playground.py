import marimo

__generated_with = "0.11.13"
app = marimo.App(width="full")


@app.cell
def _():
    from dataclasses import asdict

    import polars as pl

    from threads import Threads
    from pprint import pp
    return Threads, asdict, pl, pp


@app.cell
def _(Threads):
    threads = Threads()
    threads
    return (threads,)


@app.cell
def _():
    # posts, cursor_before, cursor_after = threads.get_threads(
    #     limit=100,
    #     since="2025-02-11",
    # )
    # print("before:", cursor_before)
    # print("after:", cursor_after)
    # pl.from_dicts([asdict(p) for p in posts])[["id", "timestamp", "text"]]
    return


@app.cell
def _(asdict, pl, threads):
    import datetime
    from dateutil.relativedelta import relativedelta
    today = datetime.date.today()
    yesterday = today + relativedelta(days=-1)

    posts=threads.get_all_posts(since=yesterday.isoformat())
    pl.from_dicts([asdict(p) for p in posts])[["id", "timestamp", "text", "replied_to", ]]
    return datetime, posts, relativedelta, today, yesterday


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
