# coding=utf-8
from __future__ import unicode_literals, print_function
from itertools import groupby

import attr
from clldutils.path import Path
from clldutils.text import split_text
from clldutils.misc import slug
from csvw.dsv import reader
from pycldf.sources import Source
from pylexibank.dataset import Language, Lexeme, Concept, Dataset as BaseDataset


@attr.s
class UralexLanguage(Language):
    Description = attr.ib(default=None)
    Subgroup = attr.ib(default=None)


@attr.s
class UralexConcept(Concept):
    Definition = attr.ib(default=None)
    LJ_rank = attr.ib(default=None)


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
    id = 'uralex'
    dir = Path(__file__).parent
    language_class = UralexLanguage
    concept_class = UralexConcept
    lexeme_class = UralexLexeme

    def cmd_download(self, **kw):
        pass

    def _read(self, what):
        return reader(self.raw / '{0}.tsv'.format(what), dicts=True, delimiter='\t')

    def cmd_install(self, **kw):
        """
        Convert the raw data to a CLDF dataset.

        Use the methods of `pylexibank.cldf.Dataset` after instantiating one as context:

        >>> with self.cldf as ds:
        ...     ds.add_sources(...)
        ...     ds.add_language(...)
        ...     ds.add_concept(...)
        ...     ds.add_lexemes(...)
        """
        with self.cldf as ds:
            ds.add_sources(self.raw.read('Citations.bib'))
            for src in self._read('Citation_codes'):
                if src['type'] == 'E':
                    ds.add_sources(Source('misc', src['ref_abbr'], author=src['original_reference']))

            for l in self._read('Languages'):
                ds.add_language(
                    ID=l['lgid3'],
                    Name=l['language'],
                    Glottocode=self.glottolog.glottocode_by_iso.get(l['ISO-639-3']),
                    Description=l['Description'],
                    Subgroup=l['Subgroup'],
                    ISO639P3code=l['ISO-639-3'])

            #"mng_item"	"LJ_rank"	"uralex_mng"	"definition"
            for c in self._read('Meanings'):
                ds.add_concept(
                    ID=c['mng_item'],
                    Name=c['uralex_mng'],
                    Definition=c['definition'],
                    LJ_rank=c['LJ_rank'],
                )
            for (cid, cogid), ll in groupby(
                    sorted(self._read('Data'), key=lambda i: (i['mng_item'], i['cogn_set'])),
                    lambda i: (i['mng_item'], i['cogn_set'])):
                for l in ll:
                    kw = dict(
                        Value=l['item'],
                        Language_ID=l['lgid3'],
                        Parameter_ID=cid,
                        Comment=l['general_notes'],
                        Source=[slug(rid, lowercase=False) for rid in split_text(l['ref_abbr'], ',', strip=True)],
                    )
                    kw.update({
                        k: l[k] for k in
                        ['item_UPA', 'item_IPA', 'form_set', 'age_term_pq', 'age_term_aq', 'borr_source', 'borr_qual',
                         'etym_notes', 'glossing_notes']})

                    for lex in ds.add_lexemes(**kw):
                        if cogid != '?':
                            ds.add_cognate(lexeme=lex, Cognateset_ID='{0}-{1}'.format(cid, cogid))
