import polars as pl
import requests
import random
import jellyfish

# read the CSV as dataframe
df = pl.read_csv('./data/data.csv', encoding='windows-1252', separator=';', infer_schema_length=10000)

# open alex URL
url = 'https://api.openalex.org/authors?filter=affiliations.institution.country_code:BR,display_name.search:'

# picks a random author from the dataframe
autor_random = random.choice(df)

# search for their name in the openalex api
res = requests.get(url + autor_random['NM_DOCENTE'][0])

if res.status_code == 200:
    # applies fuzz methods to name matching
    n1 = autor_random['NM_DOCENTE'][0].title()

    data = []
    for r in res.json()['results']:
        n2 = r['display_name'].title()
        data.append([n1, n2, jellyfish.levenshtein_distance(n1, n2), 'levenshtein_distance'])

        data.append([n1, n2, jellyfish.damerau_levenshtein_distance(n1, n2), 'damerau_levenshtein_distance'])
        
        data.append([n1, n2, jellyfish.jaro_winkler_similarity(n1, n2), 'jaro_winkler_similarity'])

    outdf = pl.DataFrame(data, schema=["Name1", "Name2", "Score", "Method"], strict=False, orient='row')
    print(outdf)
else:
    print(f'Falha na requisição: {res.status_code}')