import re
import pathlib
import itertools

import attr
from clldutils.misc import slug
from clldutils.text import split_text
from csvw.dsv import iterrows
from pycldf.sources import Source
from pybtex.database import parse_string
from pylexibank import Language, Lexeme, Concept, Dataset as BaseDataset, LexibankMetadata

NULL_ITEMS = [
    '[Form not found]',  # (309x)
    '[Not reconstructable]',  # (142x)
    '[No equivalent]',
]

# We fix a couple of misspelt bibkeys:
BIBKEYS = {
    'Sammalahti1998': 'Sammallahti1998',
    'Sammalahti1999': 'Sammallahti1999',
    'Sammalahti2001': 'Sammallahti2001',
    'Holopainenetal2017': 'Holopainen2017',
    'Zaizc2006': 'Zaicz2006',
    'Zaics2006': 'Zaicz2006',
    'Koponen1998': 'koponenetelaviron1998',
    'KoivulKoivulehto1991': 'Koivulehto1991',
    'VanPareren2009': 'vanPareren2009',
}

def bibkeys(s):
    s = re.sub(r', (?P<year>[0-9]{4})', lambda m: ' ' + m.group('year'), s)
    s = s.replace('Sammallahti1998Lehtiranta1989', 'Sammallahti1998, Lehtiranta1989')
    res = [slug(rid, lowercase=False) for rid in split_text(s, ",", strip=True)]
    return [BIBKEYS.get(k, k) for k in res]


@attr.s
class UralexMetadata(LexibankMetadata):
    def markdown(self):
        md = LexibankMetadata.markdown(self)
        before, desc, after = md.partition('\n## Description')
        assert desc
        return ''.join([
            before,
            """
When you are using UraLex 2.0, you should also cite the following papers which introduce the dataset:

> De Heer, Mervi; Blokland, Rogier; Dunn, Michael; Vesakoski, Outi. (submitted manuscript). “Loanwords in basic vocabulary as an indicator of borrowing profiles.”

and

> Syrjänen, Kaj; Maurits, Luke; Leino, Unni; Honkola, Terhi; Rota, Jadranka & Vesakoski, Outi. (submitted manuscript). “Crouching TIGER, Hidden Structure: Exploring the nature of linguistic data using TIGER values.”

""",
            desc,
            '\n\n',
            "The dataset is described in [uralex_documentation.md](uralex_documentation.md).",
            after,
        ])


@attr.s
class UralexLanguage(Language):
    Description = attr.ib(
        default=None,
        metadata={'dc:description': 'Additional language description.'}
    )
    Subgroup = attr.ib(
        default=None,
        metadata={'dc:description': 'Traditional subgroup of the language.'}
    )


@attr.s
class UralexConcept(Concept):
    Definition = attr.ib(
        default=None,
        metadata={'dc:description': 'Verbose definition of a meaning.'}
    )
    LJ_rank = attr.ib(
        default=None,
        converter=lambda s: None if s == '-' else int(s),
        metadata={
            'null': ['-'],
            'datatype': 'integer',
            'dc:description':
                'Leipzig-Jakarta rank, included for meanings belonging to either WOLD401-500 or Leipzig-Jakarta.'}
    )
    WOLD401_500_rank = attr.ib(
        default=None,
        metadata={'dc:description': 'Rank in WOLD401-500 401-500, see Lehtinen et al. (2014).'}
    )
    Ura100 = attr.ib(
        default=None,
        metadata={
            'datatype': {'base': 'boolean', 'format': 'yes|no'},
            'dc:description':
                'Present in Ura100 list - '
                'A list for stable Uralic vocabulary, based on information from 17 languages and 226 meanings covered '
                'by the first version of the dataset. Used in Syrjänen et al. (2013), Honkola et al. (2013) and '
                'Lehtinen et al. (2014).'}
    )
    Swadesh100 = attr.ib(
        default=None,
        metadata={
            'datatype': {'base': 'boolean', 'format': 'yes|no'},
            'dc:description': 'Present in 100-item Swadesh list.'}
    )
    Swadesh207 = attr.ib(
        default=None,
        metadata={
            'datatype': {'base': 'boolean', 'format': 'yes|no'},
            'dc:description': 'Present in combined meanings of Swadesh100 and Swadesh200.'}
    )
    Leipzig_Jakarta = attr.ib(
        default=None,
        metadata={
            'datatype': {'base': 'boolean', 'format': 'yes|no'},
            'dc:description': "Present in 100-item Leipzig-Jakarta list (101 items due to the separation "
                                    "of 'foot' and 'leg' in Uralic languages)."}
    )
    WOLD401_500 = attr.ib(
        default=None,
        metadata={
            'datatype': {'base': 'boolean', 'format': 'yes|no'},
            'dc:description': 'Present in meanings ranked 401-500 in the WOLD database, used in '
                                    'Lehtinen et al. (2014).'}
    )
    Fullbasic = attr.ib(
        default=None,
        metadata={
            'datatype': {'base': 'boolean', 'format': 'yes|no'},
            'dc:description': 'Present in combined meanings of Swadesh100, Swadesh200 and Leipzig-Jakarta.'}
    )
    Swadesh200 = attr.ib(
        default=None,
        metadata={
            'datatype': {'base': 'boolean', 'format': 'yes|no'},
            'dc:description': 'Present in 200-item Swadesh list.'}
    )


@attr.s
class UralexLexeme(Lexeme):
    item_UPA = attr.ib(
        default=None,
        metadata={'dc:description': 'Phonetic transcription in Uralic Phonetic Alphabet (included for 11 languages).'}
    )
    item_IPA = attr.ib(
        default=None,
        metadata={
            'dc:description': 'Phonetic transcription in International Phonetic Alphabet (included for 16 languages).'}
    )
    form_set = attr.ib(
        default=None,
        converter=lambda s: None if s == '?' else int(s),
        metadata={
            'null': ['?'],
            'datatype': {'base': 'integer', 'minimum': 0},
            'dc:description':
                "Correlate set (historical connection based on borrowing or cognacy), marked with positive integers. "
                "For [No equivalent] items the field is marked with '0'; for [Form not found] and [Not reconstructable]"
                " items the field is marked with '?'."}
    )
    etym_notes = attr.ib(
        default=None,
        metadata={'dc:description': 'Notes related to etymology of the lexeme.'}
    )
    glossing_notes = attr.ib(
        default=None,
        metadata={'dc:description': 'Notes related to the meaning of the lexeme.'}
    )


class Dataset(BaseDataset):
    id = "uralex"
    dir = pathlib.Path(__file__).parent
    language_class = UralexLanguage
    concept_class = UralexConcept
    lexeme_class = UralexLexeme
    metadata_cls = UralexMetadata

    def _read(self, what):
        return iterrows(self.raw_dir / "{0}.tsv".format(what), dicts=True, delimiter="\t")

    def cmd_makecldf(self, args):
        args.writer.add_sources(self.raw_dir.read("Citations.bib"))
        bib = parse_string(self.raw_dir.read('Borrowing_references.bib'), 'bibtex')
        for k, v in bib.entries.items():
            args.writer.add_sources(Source.from_entry(slug(k, lowercase=False), v))

        args.writer.cldf.add_component(
            'BorrowingTable',
            {
                'name': 'Likelihood',
                'dc:description': 'Likelihood of borrowing (*possible*, *probable* or *clear*).',
                'datatype': {'base': 'string', 'format': 'possible|clear|probable'}
            },
            {
                'name': 'SourceLanguoid',
                'dc:description': 'Borrowing source of lexeme.',
            }
        )
        args.writer.cldf['FormTable', 'form'].required = False
        args.writer.cldf['FormTable', 'value'].null = NULL_ITEMS
        args.writer.cldf['FormTable', 'value'].required = False
        args.writer.cldf['FormTable', 'value'].common_props['dc:description'] = \
            "Lexeme data. Contains a lexeme or '[No equivalent]': no suitable equivalent for a meaning exists), " \
            "'[Form not found]': no suitable equivalent was found, or '[Not reconstructable]': non-recontructable " \
            "meanings in Proto-Uralic."

        for src in self._read("Citation_codes"):
            if src["type"] == "E":
                args.writer.add_sources(
                    Source("misc", src["ref_abbr"], author=src["original_reference"])
                )

        glottocodes = {language["ID"]: language["Glottocode"] for language in self.languages}
        for language in self._read("Languages"):
            glottocode = glottocodes.get(language["lgid3"])
            if not glottocode:
                glottocode = self.glottolog.glottocode_by_iso.get(language["ISO-639-3"])
            args.writer.add_language(
                ID=language["lgid3"],
                Name=language["language"],
                Glottocode=glottocode,
                Description=language["Description"],
                Subgroup=language["Subgroup"],
                ISO639P3code=language["ISO-639-3"],
            )

        inlists = {r['mng_item']: r for r in self._read('Meaning_lists')}
        attrs = [k for k in attr.fields_dict(UralexConcept).keys() if k != 'LJ_rank']
        for concept in self.concepts:
            if concept['ID'] in inlists:
                memberships = {
                    k.replace('-', '_'): v == '1'
                    for k, v in inlists[concept['ID']].items() if k.replace('-', '_') in attrs}
                concept.update(memberships)
            args.writer.add_concept(**concept)

        for (cid, cogid), ll in itertools.groupby(
            sorted(self._read("Data"), key=lambda i: (i["mng_item"], i["cogn_set"])),
            lambda i: (i["mng_item"], i["cogn_set"]),
        ):
            for language in ll:
                if language['item'] in NULL_ITEMS:
                    language['etym_notes'] = language['etym_notes'] + language['item']
                kw = dict(
                    Value=language["item"],
                    Language_ID=language["lgid3"],
                    Parameter_ID=cid,
                    Comment=language["general_notes"],
                    Source=[
                        slug(rid, lowercase=False)
                        for rid in split_text(language["ref_abbr"], ",", strip=True)
                    ],
                )
                kw.update(
                    {
                        k: language[k]
                        for k in [
                            "item_UPA",
                            "item_IPA",
                            "form_set",
                            "etym_notes",
                            "glossing_notes",
                        ]
                    }
                )

                for i, lex in enumerate(args.writer.add_lexemes(**kw)):
                    lex['Form'] = None if lex['Form'] in NULL_ITEMS else lex['Form']
                    if cogid not in ["?", "0"]:
                        args.writer.add_cognate(
                            lexeme=lex, Cognateset_ID="{0}-{1}".format(cid, cogid)
                        )
                    if language['borr_qual']:
                        c = ': borrowed to Pre-Permic'
                        ref = language['ref_borr']
                        if c in ref:
                            comment = c[1:].strip()
                            ref = ref.replace(c, '')
                        else:
                            comment = None
                        args.writer.objects['BorrowingTable'].append(dict(
                            ID=lex['ID'],
                            Target_Form_ID=lex['ID'],
                            SourceLanguoid=language['borr_source'],
                            Likelihood=language['borr_qual'],
                            Source=bibkeys(ref),
                            Comment=comment,
                        ))