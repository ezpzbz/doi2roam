import click
import requests
import pandas as pd

__author__ = "pzarabadip"
__version__ = "0.1"
__maintainer__ = "Pezhman Zarabadi-Poor"
__email__ = "pzarabadip@gmail.com"
__status__ = "Development"
__date__ = "April 2021"

df = pd.read_csv('./journal_abbreviations_acs.csv',delimiter=';',header=None)
df.rename(columns={0: "long_name", 1: "short_name"},inplace=True)

def get_json(doi):
    url = f'http://api.crossref.org/works/{doi}'
    resp = requests.get(url)
    found = False if resp.status_code != 200 else True
    entry_json = resp.json()
    return found, entry_json

def find_validate(doi):
    found = False
    try:
        found, entry = get_json(doi)
    except:
        raise ValueError('Could not perform the request!')
    
    if found:
        return entry

def synthesize_roam_import(doi):
    
    json = find_validate(doi)
#     title
    t = json['message']['title'][0]
    title = f'- {t}\n'
#     Abstract
    if 'abstract' in json['message'].keys():
        abst = json['message']['abstract'][0]
        abstract = f'- Abstract:\n\t- {abst}'
    else:
        abstract = f'- Abstract:\n\t- \n'
    
#     References - Authors
    ref_base = '- Reference:\n'
    auth_base = '\t- Authors:\n'
    
    author_list = json['message']['author']
    a_list = []
    for index,a in enumerate(author_list):
        if index == 0:
            filename_author = a['family']
        given = a['given']
        family = a['family']
        item = f'[[{given} {family}]]'
        auth_base += '\t\t- '+item +'\n'

    ref = ref_base + auth_base 
#     Reference - Journal
    journal = json['message']['container-title']
    abbr = df[df['long_name'] == journal[0]]['short_name'].values[0]
    filename_journal = abbr.replace(' ','').replace('.','')

    journal = f'\t- Journal:\n\t\t- [[{journal[0]}]] [[{abbr}]]\n'
#     Url
    if 'url' in json['message'].keys():
        u = json['message']['url']
    elif 'URL' in json['message'].keys():
        u = json['message']['URL']
    url = f'\t- URL:\n\t\t- {u}\n'
    
    empty_fields = '- Notes:\n- Summary:\n- Concepts:\n- Keywords:\n'
    
    filename_year = json['message']['created']['date-parts'][0][0]
    
    filename = f'{filename_author}EtAl_{filename_journal}{filename_year}'
    
    entry = title + abstract + ref + journal + url + empty_fields
    
    print('\n'+filename+'\n')
    print(entry)
    
    return filename, entry

@click.command('cli')
@click.argument('doi')
def cli(doi):
    filename, entry = synthesize_roam_import(doi)
    with open(f'{filename}.md','w') as handler:
        handler.write(entry)
    
if __name__ == '__main__':
    cli()

        