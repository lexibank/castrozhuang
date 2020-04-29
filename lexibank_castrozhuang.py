from __future__ import unicode_literals, print_function
from collections import OrderedDict, defaultdict

import attr
from pathlib import Path
from clldutils.misc import slug

from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import Concept, Language, FormSpec

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
    Family = attr.ib(default='Tai-Kadai')
    SubGroup = attr.ib(default='Zhuang')
    ISO = attr.ib(default=None)
    Location = attr.ib(default=None)


class Dataset(BaseDataset):
    id = 'castrozhuang'
    dir = Path(__file__).parent
    concept_class = HConcept
    language_class = HLanguage
    
    def cmd_makecldf(self, args):

        args.writer.add_sources()
        wl = Wordlist(self.dir.joinpath('raw', 'wordlist.tsv').as_posix())
        langs = {} # need for checking later
        concepts = {}

        strip_concept = lambda x: x.replace(' ', '').replace('*', '')

        for concept in self.conceptlists[0].concepts.values():
            args.writer.add_concept(
                    ID=concept.id,
                    Name=concept.english,
                    Chinese_Gloss=strip_concept(concept.attributes['chinese']),
                    Concepticon_ID=concept.concepticon_id,
                    Concepticon_Gloss=concept.concepticon_gloss
                    )
            concepts[strip_concept(concept.attributes['chinese'])] = concept.id
        langs = {k['ChineseName']: k['ID'] for k in self.languages}
        args.writer.add_languages()

        bads = []
        for idx in tqdm(wl, desc='cldfify'):

            args.writer.add_form_with_segments(
               Language_ID=langs[wl[idx, 'doculect']],
               Parameter_ID=concepts[strip_concept(wl[idx, 'concept'])],     
               Value=wl[idx, 'value'],
               Form=wl[idx, 'form'],
               Segments=wl[idx, 'tokens'],
               Source=['Castro2010a']
               )



