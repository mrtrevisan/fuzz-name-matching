import polars as pl
import requests
import recordlinkage
import unicodedata

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')

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

# Fetch data for each random author
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

indexer = recordlinkage.Index()
indexer.block('nome') 

candidate_links = indexer.index(capes_df.to_pandas(), openA_df.to_pandas())

compare = recordlinkage.Compare()
compare.string('nome', 'nome', method='jarowinkler', threshold=0.75, label='nome')
features = compare.compute(candidate_links, capes_df.to_pandas(), openA_df.to_pandas())

matches = features[features.sum(axis=1) > 0]

results = []
for index in matches.index:
    name1 = capes_df.to_pandas().loc[index[0], 'nome']
    name2 = openA_df.to_pandas().loc[index[1], 'nome']
    results += [[index[0], name1, '<=>', index[1], name2]]

print("Matches:")
res_df = pl.DataFrame(results, schema=['Idx Capes', 'Nome Capes', ' ', 'Idx OpenAlex', 'Nome OpenAlex'], orient="row").with_row_index()
print(res_df)