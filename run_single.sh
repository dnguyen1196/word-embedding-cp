#!/usr/bin/env bash
min_count = 1000
num_articles = 1e5
embedding_dim = 300
python3 -m pdb -c continue test_gensim.py --method=random --min_count=$(min_count) --num_articles=$(num_articles) --embedding_dim=$(embedding_dim)