from threads import Threads


def main():
    threads = Threads()
    print(threads.id)
    posts = threads.get_threads(
        limit=10,
        since="2025-02-11",
        until="2025-02-12",
    )


main()
