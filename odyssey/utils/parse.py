from joblib import Memory
import parso
memory = Memory(cachedir=".", verbose=0)


@memory.cache
def parso_parse(code):
    return parso.parse(code)
