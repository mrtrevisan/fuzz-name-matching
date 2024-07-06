import polars as pl
import requests
import random
from thefuzz import fuzz

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
        data.append([n1, n2, fuzz.ratio(n1, n2), 'simple ratio'])

        data.append([n1, n2, fuzz.partial_ratio(n1, n2), 'partial ratio'])
        
        data.append([n1, n2, fuzz.token_sort_ratio(n1, n2), 'token sort ratio'])

        data.append([n1, n2, fuzz.token_set_ratio(n1, n2), 'token set ratio'])

    outdf = pl.DataFrame(data, schema=["Name1", "Name2", "Score", "Method"], strict=False, orient='row')
    print(outdf)
else:
    print(f'Falha na requisição: {res.status_code}')
