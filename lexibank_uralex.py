import pathlib
import itertools

import attr
from clldutils.misc import slug
from clldutils.text import split_text
from csvw.dsv import reader
from pycldf.sources import Source
from pylexibank import Language, Lexeme, Concept, Dataset as BaseDataset


@attr.s
class UralexLanguage(Language):
    Description = attr.ib(default=None)
    Subgroup = attr.ib(default=None)


@attr.s
class UralexConcept(Concept):
    Definition = attr.ib(default=None)
    LJ_rank = attr.ib(default=None)
    WOLD401_500_rank = attr.ib(default=None)


@attr.s
class UralexLexeme(Lexeme):
    item_UPA = attr.ib(default=None)
    item_IPA = attr.ib(default=None)
    form_set = attr.ib(default=None)
    age_term_pq = attr.ib(default=None)
    age_term_aq = attr.ib(default=None)
    borr_source = attr.ib(default=None)
    borr_qual = attr.ib(default=None)
    etym_notes = attr.ib(default=None)
    glossing_notes = attr.ib(default=None)


class Dataset(BaseDataset):
    id = "uralex"
    dir = pathlib.Path(__file__).parent
    language_class = UralexLanguage
    concept_class = UralexConcept
    lexeme_class = UralexLexeme

    def _read(self, what):
        return reader(self.raw_dir / "{0}.tsv".format(what), dicts=True, delimiter="\t")

    def cmd_makecldf(self, args):
        args.writer.add_sources(self.raw_dir.read("Citations.bib"))
        for src in self._read("Citation_codes"):
            if src["type"] == "E":
                args.writer.add_sources(
                    Source("misc", src["ref_abbr"], author=src["original_reference"])
                )

        glottocodes = {l["ID"]: l["Glottocode"] for l in self.languages}
        for l in self._read("Languages"):
            glottocode = glottocodes.get(l["lgid3"])
            if not glottocode:
                glottocode = self.glottolog.glottocode_by_iso.get(l["ISO-639-3"])
            args.writer.add_language(
                ID=l["lgid3"],
                Name=l["language"],
                Glottocode=glottocode,
                Description=l["Description"],
                Subgroup=l["Subgroup"],
                ISO639P3code=l["ISO-639-3"],
            )

        for concept in self.concepts:
            args.writer.add_concept(**concept)

        for (cid, cogid), ll in itertools.groupby(
            sorted(self._read("Data"), key=lambda i: (i["mng_item"], i["cogn_set"])),
            lambda i: (i["mng_item"], i["cogn_set"]),
        ):
            for l in ll:
                kw = dict(
                    Value=l["item"],
                    Language_ID=l["lgid3"],
                    Parameter_ID=cid,
                    Comment=l["general_notes"],
                    Source=[
                        slug(rid, lowercase=False)
                        for rid in split_text(l["ref_abbr"], ",", strip=True)
                    ],
                )
                kw.update(
                    {
                        k: l[k]
                        for k in [
                            "item_UPA",
                            "item_IPA",
                            "form_set",
                            "age_term_pq",
                            "age_term_aq",
                            "borr_source",
                            "borr_qual",
                            "etym_notes",
                            "glossing_notes",
                        ]
                    }
                )

                for lex in args.writer.add_lexemes(**kw):
                    if cogid != "?":
                        args.writer.add_cognate(lexeme=lex, Cognateset_ID="{0}-{1}".format(cid, cogid))
