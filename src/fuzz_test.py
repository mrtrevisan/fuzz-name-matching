import polars as pl
import requests
import random
from thefuzz import fuzz

# read the CSV as dataframe
df = pl.read_csv('./data/data.csv', encoding='utf-8', separator=';', infer_schema_length=10000)

# open alex URL
url = 'https://api.openalex.org/authors?filter=affiliations.institution.country_code:BR,display_name.search:'

# picks a random author from the dataframe
autor_random = random.choice(df)

# search for their name in the openalex api
res = requests.get(url + autor_random['NM_DOCENTE'][0])

if res.status_code == 200:
    # applies fuzz methods to name matching
    with open('out/result.csv', 'w', encoding='utf-8') as out_file:
        n1 = autor_random['NM_DOCENTE'][0].title()

        for r in res.json()['results']:
            n2 = r['display_name'].title()
            out_file.write(f"{n1}|{n2}|{str(fuzz.ratio(n1, n2))}|{'simple ratio'}\n")

            out_file.write(f"{n1}|{n2}|{str(fuzz.partial_ratio(n1, n2))}|{'partial ratio'}\n")
            
            out_file.write(f"{n1}|{n2}|{str(fuzz.token_sort_ratio(n1, n2))}|{'token sort ratio'}\n")

            out_file.write(f"{n1}|{n2}|{str(fuzz.token_set_ratio(n1, n2))}|{'token set ratio'}\n")
            
            out_file.write("\n")
else:
    print(f'Falha na requisição: {res.status_code}')
