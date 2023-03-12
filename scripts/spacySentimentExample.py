import spacy
import textacy
from spacytextblob.spacytextblob import SpacyTextBlob

# https://realpython.com/natural-language-processing-spacy-python/
# https://importsem.com/evaluate-sentiment-analysis-in-bulk-with-spacy-and-python/


# load the language callable object
nlp = spacy.load('en_core_web_sm')
nlp.add_pipe('spacytextblob')

my_doc = nlp(
    """This is my document about absolutely nothing.
    I really don't like having nothing to say.
    """
)
sentiment = my_doc._.blob.polarity
sentiment = round(sentiment,2)

if sentiment > 0:
  sent_label = "Positive"
else:
  sent_label = "Negative"

print(f"Sentiment, score: {sentiment}, label: {sent_label}")

for sentence in list(my_doc.sents):
    print(f"{sentence[:3]}...")

# for item in dir(my_doc):
#     print(item)

for noun_phrase in my_doc.noun_chunks:
    print(noun_phrase)