# coding=utf-8
from __future__ import unicode_literals, print_function
from itertools import groupby

import attr
from clldutils.path import Path
from clldutils.text import split_text
from clldutils.misc import slug
from csvw.dsv import reader
from pycldf.sources import Source
from pylexibank.dataset import Language, Concept, Dataset as BaseDataset


@attr.s
class UralexLanguage(Language):
    Description = attr.ib(default=None)
    Subgroup = attr.ib(default=None)


@attr.s
class UralexConcept(Concept):
    Definition = attr.ib(default=None)


class Dataset(BaseDataset):
    id = 'uralex'
    dir = Path(__file__).parent
    language_class = UralexLanguage
    concept_class = UralexConcept

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
            for src in self._read('Citation_codes'):
                refid = slug(src['ref_abbr'], lowercase=False)
                if src['type'] == 'E':
                    src = Source('misc', refid, author=src['original_reference'])
                else:
                    src = Source('book', refid, title=src['original_reference'])
                ds.add_sources(src)
            #"lgid3"	"language"	"ASCII_name"	"ISO-639-3"	"Description"	"Subgroup"
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
                )
            # "item_UPA"
            # "item_IPA"
            # "form_set"
            # "cogn_set"
            # "age_term_pq"
            # "age_term_aq"
            # "borr_source"
            # "borr_qual"
            # "etym_notes"
            # "glossing_notes"
            for (cid, cogid), ll in groupby(
                    sorted(self._read('Data'), key=lambda i: (i['mng_item'], i['cogn_set'])),
                    lambda i: (i['mng_item'], i['cogn_set'])):
                for l in ll:
                    for lex in ds.add_lexemes(
                        Value=l['item'],
                        Language_ID=l['lgid3'],
                        Parameter_ID=cid,
                        Comment=l['general_notes'],
                        Source=[slug(rid, lowercase=False) for rid in split_text(l['ref_abbr'], ',', strip=True)],
                    ):
                        if cogid != '?':
                            ds.add_cognate(lexeme=lex, Cognateset_ID='{0}-{1}'.format(cid, cogid))
