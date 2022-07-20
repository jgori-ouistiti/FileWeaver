import glob
import os

import re
import yake
from pylatexenc.latex2text import LatexNodes2Text

import gensim
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize

text = []

#globing our books
folder = 'books/openintro-statistics/'
books = glob.glob(folder + "**/*.tex", recursive=True)

#get our training books
for i, b in enumerate(books) :
    f = open(b, "r")
    text.append(LatexNodes2Text().latex_to_text(f.read().lower()))
tagged_data = [TaggedDocument(words=word_tokenize(_d.lower()), tags=[str(i)]) for i, _d in enumerate(text)]
print(f"tagged {tagged_data}")

#training
model = Doc2Vec()
model.build_vocab(tagged_data)
model.train(tagged_data, total_examples=model.corpus_count, epochs=50)

print(f"most similar from 0 is {model.docvecs.most_similar([0])}")

#infer vectors on remaining books
for i, b in enumerate(books):
    if i>=5:
        print(b)
        f = open(b, "r")
        tokenized = LatexNodes2Text().latex_to_text(f.read().lower()) 
        text = word_tokenize(tokenized)
        print(model.infer_vector(text))