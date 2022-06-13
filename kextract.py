import yake
from pylatexenc.latex2text import LatexNodes2Text
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation

f = open("math_textbook_en.tex", "r")

lines = f.readlines()
text = " ".join(l for l in lines)
w = LatexNodes2Text().latex_to_text(text)

vectorizer = CountVectorizer()
X = vectorizer.fit_transform([w])
#print(f"Vocabulary : {X.vocabulary_}")


kw_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9)
keywords = kw_extractor.extract_keywords(text)
for k in keywords :
    print(k)

lda = LatentDirichletAllocation(n_components=5,random_state=101)

lda_fit  = lda.fit(X)
# understanding each topics top 10 common words
for id_value, value in enumerate(lda_fit.components_):
    print(f"The topic would be {id_value}")
    print([vectorizer.get_feature_names()[index] for index in value.argsort()   [-10:]])
    print("\n")
