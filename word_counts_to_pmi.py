import pickle
from test_gensim import GensimSandbox, PMIGatherer

pickedfile = "./3D_pmi_gatherer"

# TODO: why no negative PMI?
# TODO:

with open(pickedfile, "rb") as f:
    pmi_gatherer = pickle.load(f, encoding="latin1")
    num_words = pmi_gatherer.vocab_len

    i = 0
    for j in range(num_words):
        for k in range(num_words):
            pmi = pmi_gatherer.PMI(i, j, k)
            if pmi != 0:
                print("({},{},{}) -> ".format(i, j, k), pmi)

