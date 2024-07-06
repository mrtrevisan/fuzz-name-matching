import polars as pl
import requests
import fasttext
import fasttext.util
from scipy.spatial.distance import cosine

df = pl.read_csv('./data/data.csv', encoding='windows-1252', separator=';', infer_schema_length=10000)

def fetch_OpenAlex(autor):
    url = 'https://api.openalex.org/authors?filter=affiliations.institution.country_code:BR,display_name.search:'

    res = requests.get(url + autor)
    if res.status_code == 200:
        return [r['display_name'].title() for r in res.json()['results']]
    else:
        return None

num = 5
capes_authors = [ n.title() for n in df['NM_DOCENTE'].sample(num).to_list()]

openAlex_authors = []
for author in capes_authors:
    data = fetch_OpenAlex(author)
    if data:
        openAlex_authors += data

capes_df = pl.DataFrame(capes_authors, schema=["nome"])
openA_df = pl.DataFrame(openAlex_authors, schema=["nome"])

print("Capes Sample:")
print(capes_df.with_row_index())
print("OpenAlex Search:")
print(openA_df.with_row_index())

# Load a pre-trained FastText model
fasttext.util.download_model('pt', if_exists='ignore')
fasttext_model = fasttext.load_model('cc.pt.300.bin')

def get_embedding(name):
    return fasttext_model.get_sentence_vector(name)

embedding = map(get_embedding, capes_df['nome'].to_list())
capes_df = capes_df.with_columns(
    pl.Series(name="embedding", values=embedding)
)

embedding = map(get_embedding, openA_df['nome'].to_list())
openA_df = openA_df.with_columns(
    pl.Series(name="embedding", values=embedding)
)

def cosine_similarity(a, b):
    return 1 - cosine(a, b)

matches = []
threshold = 0.85

for capes_name, capes_emb in zip(capes_df['nome'], capes_df['embedding']):
    for oa_name, oa_emb in zip(openA_df['nome'], openA_df['embedding']):
        similarity = cosine_similarity(capes_emb, oa_emb)
        if similarity > threshold:
            matches.append((capes_name, oa_name, similarity))

print("Matches:")
matches_df = pl.DataFrame(matches, schema=['Nome Capes', 'Nome OpenAlex', 'Similarity'], orient="row").with_row_index()
print(matches_df)