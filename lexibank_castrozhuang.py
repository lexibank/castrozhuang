from pathlib import Path

import attr
import lingpy
import pylexibank


@attr.s
class HConcept(pylexibank.Concept):
    Chinese_Gloss = attr.ib(default=None)


@attr.s
class HLanguage(pylexibank.Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    ChineseName = attr.ib(default=None)
    Family = attr.ib(default="Tai-Kadai")
    SubGroup = attr.ib(default="Zhuang")
    Location = attr.ib(default=None)


class Dataset(pylexibank.Dataset):
    id = "castrozhuang"
    dir = Path(__file__).parent
    concept_class = HConcept
    language_class = HLanguage
    writer_options = dict(keep_languages=False, keep_parameters=False)

    def cmd_makecldf(self, args):

        args.writer.add_sources()
        wl = lingpy.Wordlist(self.dir.joinpath("raw", "wordlist.tsv").as_posix())
        concepts = {}
        strip_concept = lambda x: x.replace(" ", "").replace("*", "")

        for concept in self.conceptlists[0].concepts.values():
            args.writer.add_concept(
                ID=concept.id,
                Name=concept.english,
                Chinese_Gloss=strip_concept(concept.attributes["chinese"]),
                Concepticon_ID=concept.concepticon_id,
                Concepticon_Gloss=concept.concepticon_gloss,
            )
            concepts[strip_concept(concept.attributes["chinese"])] = concept.id
        langs = {k["ChineseName"]: k["ID"] for k in self.languages}
        args.writer.add_languages()

        for idx in pylexibank.progressbar(wl, desc="cldfify"):

            args.writer.add_form_with_segments(
                Language_ID=langs[wl[idx, "doculect"]],
                Parameter_ID=concepts[strip_concept(wl[idx, "concept"])],
                Value=wl[idx, "value"],
                Form=wl[idx, "form"],
                Segments=wl[idx, "tokens"],
                Source=["Castro2010a"],
            )
