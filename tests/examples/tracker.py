from mkreports.stack import Tracker


def b():
    return 1


def a():
    return b()


if __name__ == "__main__":
    t = Tracker()
    with t:
        a()
        print("End of context")

    print(str(t.tree.md_tree(highlight=True).to_markdown(None)))
