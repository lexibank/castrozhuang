from __future__ import unicode_literals, print_function
from collections import OrderedDict, defaultdict

import attr
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.dataset import Concept, Language

from lingpy import *
from tqdm import tqdm

@attr.s
class HConcept(Concept):
    Chinese_Gloss = attr.ib(default=None)

@attr.s
class HLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    ChineseName = attr.ib(default=None)


class Dataset(BaseDataset):
    id = 'castrozhuang'
    dir = Path(__file__).parent
    concept_class = HConcept
    language_class = HLanguage
    
    def clean_form(self, item, form):
        return form.strip().replace(' ', '_')

    def cmd_download(self, **kw):
        pass

    def cmd_install(self, **kw):

        wl = Wordlist(self.dir.joinpath('raw', 'wordlist.tsv').as_posix())
        langs = {} # need for checking later
        concepts = {}

        strip_concept = lambda x: x.replace(' ', '').replace('*', '')

        with self.cldf as ds:

            for concept in self.conceptlist.concepts.values():
                ds.add_concept(
                        ID=concept.id,
                        Name=concept.english,
                        Chinese_Gloss=strip_concept(concept.attributes['chinese']),
                        Concepticon_ID=concept.concepticon_id,
                        Concepticon_Gloss=concept.concepticon_gloss
                        )
                concepts[strip_concept(concept.attributes['chinese'])] = concept.id
            for language in self.languages:
                ds.add_language(
                        ID=language['ID'],
                        Glottocode=language['Glottolog'],
                        Name=language['Name'],
                        Latitude=language['Latitude'],
                        Longitude=language['Longitude'],
                        ChineseName=language['ChineseName']
                        )
                langs[language['ChineseName']] = language['ID']

            ds.add_sources(*self.raw.read_bib())
            bads = []
            for idx in tqdm(wl, desc='cldfify'):
                #if wl[idx, 'concept'].replace(' ', '').replace('*', '') not in concepts:
                #    c = wl[idx, 'concept'].replace(' ', '').replace('*', '')
                #    if c not in bads:
                #        print(wl[idx, 'concept'])
                #    else:
                #        bads += [c]

                #else:
                ds.add_lexemes(
                   Language_ID=langs[wl[idx, 'doculect']],
                   Parameter_ID=concepts[strip_concept(wl[idx, 'concept'])], #.replace(' ', '').replace('*', '')],
                   Value=wl[idx, 'value'],
                   Form=wl[idx, 'form'],
                   Segments=wl[idx, 'tokens'],
                   Source=['Castro2010a']
                   )



