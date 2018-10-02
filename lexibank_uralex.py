# coding=utf-8
from __future__ import unicode_literals, print_function

import attr
from clldutils.path import Path
from csvw.dsv import reader
from pylexibank.dataset import Language, Concept, Dataset as BaseDataset


@attr.s
class UralexLanguage(Language):
    Description = attr.ib(default=None)


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
        #"lgid3"	"language"	"ASCII_name"	"ISO-639-3"	"Description"	"Subgroup"
        with self.cldf as ds:
            for l in self._read('Languages'):
                ds.add_language(
                    ID=l['lgid3'],
                    Name=l['language'],
                    Glottocode=self.glottolog.glottocode_by_iso.get(l['ISO-639-3']),
                    Description=l['Description'],
                    ISO639P3code=l['ISO-639-3'])

            #"mng_item"	"LJ_rank"	"uralex_mng"	"definition"
            for c in self._read('Meanings'):
                ds.add_concept(
                    ID=c['mng_item'],
                    Name=c['uralex_mng'],
                    Definition=c['definition'],
                )
            #"language"	"definition"	"uralex_mng"	"mng_item"	"lgid3"	"item"	"item_UPA"	"item_IPA"	"form_set"	"cogn_set"	"age_term_pq"	"age_term_aq"	"borr_source"	"borr_qual"	"etym_notes"	"glossing_notes"	"general_notes"	"ref_abbr"
            for l in self._read('Data'):
                ds.add_lexemes(
                    Value=l['item'],
                    Language_ID=l['lgid3'],
                    Parameter_ID=l['mng_item'],
                )
