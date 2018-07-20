from test_gensim import GensimSandbox

method="cp-s"
num_articles=1e5
embedding_dim=80
min_count=5
gpu=True

sandbox = GensimSandbox(
    method=method,
    num_articles=num_articles,
    embedding_dim=embedding_dim,
    min_count=min_count,
    gpu=gpu)

fname = "wikimodel_100000_5"
import dill

model = dill.load(open(fname, 'rb'))
sandbox.model = model
pmi_gatherer_3D = sandbox.get_pmi_gatherer(3)


import pickle
output_file = "./3D_pmi_gatherer_min_5"
pickle.dump(pmi_gatherer_3D, open(output_file, "wb"))
