# https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
def flatten(L):
    if L is None:
        return None
    for item in L:
        try:
            if type(item) is not tuple:
                yield from flatten(item)
            else:
                yield item
        except TypeError:
            yield item