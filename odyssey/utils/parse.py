from joblib import Memory
import parso
memory = Memory(location=".", verbose=0)


@memory.cache
def parso_parse(code):
    return parso.parse(code)
