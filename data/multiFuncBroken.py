def foo(bar, baz):
    return bar + baz + baz


def gux(qux):
    return qux + foo(qux, qux)
