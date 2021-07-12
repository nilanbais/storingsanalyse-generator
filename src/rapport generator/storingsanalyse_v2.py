"""
Class voor het berekenen van de verschillende van storingen per maand etc.

Nu hoor ik u denken, "waarom niet gewoon in de code cellen van een jupyter notebook?" Nou, dat zal ik u uitleggen.
De overzichtelijkheid van de notebook.
Korte uileg, maar goed.

Nu de langere uitleg:
Na het gesprek met Remko kwam er toch aan het licht dat enige manuele handelingen niet volledig weggewerkt kunnen
worden. Dit wil je in die situatie voornamelijk in de notebook laten doen, en deze dus niet 'vervuilen' met cellen
gevuld met code voor het omvormen van de data om één cijfer te kunnen presenteren. De berekening van die cijfers
worden dus in een class gedaan, er wordt ruimte bespaard, en de historische data uit de metadata kan ondergebracht
worden in dezelfde class. Dit laatste maakt het realiseren van een geüpdatte metadata.json mogelijk
(en wss gemakkelijker).

"""
import json
import os.path

import pandas as pd

from stagingfile_class import StagingFileBuilder
from metadata_storingsanalyse import MetadataStoringsAnalyse
from query_maximo_database import QueryMaximoDatabase


class StoringsAnalyse(MetadataStoringsAnalyse):

    # Class variables (callable by using class_name.var_name)
    _ld_map_path = "..\\..\\res\\location_description_map.json"  # location_description_map

    def __init__(self, project, api_key, object_structure):
        MetadataStoringsAnalyse.__init__(self, project=project)

        self._maximo = QueryMaximoDatabase(api_key, object_structure)
        self.response_data = self._maximo.response_data  # is set by get_maximo_export, default = None
        self.filename_saved_response_data = None

        self.staging_file_name = None  # set by build_staging_file
        self.staging_file_path = None  # set by get_staging_file
        self.staging_file_data = None  # set by get_staging_file

        self.meldingen = None
        self.storingen = None

        # todo: aanpassen zodat geen df maar een dict o.i.d. wordt gebruikt als dtype van de attribute
        self._ld_map = self._read_ld_map()  # df with the mapped location and description

        self.project = self.project()
        self.start_date = self.startdate()

    """
    PROTECTED MODULES
    """
    @staticmethod
    def _read_ld_map():
        """
        Module to load the data for the descriptions of the location breakdown structure numbers (LBS) and the system
        breakdown structure numbers (SBS).
        :return:
        """
        with open(os.path.relpath(StoringsAnalyse._ld_map_path), 'r') as file:
            description_data = json.load(file)
        return pd.DataFrame(description_data)

    def _get_breakdown_description(self, sbs_lbs):
        description = [self._ld_map.loc[str(index), 'description']
                       for index in range(self._ld_map.shape[0])
                       if sbs_lbs == self._ld_map.loc[str(index), 'location']]
        return description if len(description) > 0 else [""]  # To cover empty rows

    @staticmethod
    def _month_num_to_name(month_num: list):
        maand_dict = {"1": "Januari", "2": "Februari", "3": "Maart", "4": "April", "5": "Mei", "6": "Juni", "7": "Juli",
                      "8": "Augustus", "9": "September", "10": "Oktober", "11": "November", "12": "December", }
        maand = [maand_dict[str(num)] for num in month_num for key in maand_dict.keys() if str(num) == key]
        return maand

    @staticmethod
    def _isolate_di_number(asset_num_string):
        return asset_num_string.split('-')[0]

    @staticmethod
    def _order_frequency_table(freq_table):
        return {key: value for key, value in sorted(freq_table.items(), key=lambda item: item[1], reverse=True)}

    def _get_ntype(self, like_ntype):
        if like_ntype is None:
            return self.staging_file_data
        elif like_ntype.lower() in {'m', 'melding', 'meldingen'}:
            ntype = "Melding"
        elif like_ntype.lower() in {'s', 'storing', 'storingen'}:
            ntype = "Storing"
        elif like_ntype.lower() in {'i', 'incident', 'incidenten'}:
            ntype = "Incident"
        elif like_ntype.lower() in {'p', 'preventief'}:
            ntype = "Preventief"
        elif like_ntype.lower() in {'o', 'onterecht'}:
            ntype = "Onterecht"
        elif like_ntype.lower() in {"meldingen", "storing", "incident", "preventief", "onterecht"}:
            pass
        else:
            raise ValueError("Please select either \"Melding\", \"Storing\", \"Incident\", \"Preventief\", "
                             "\"Onterecht\" as like_ntype.")

        return ntype

    def _isolate_notification_type(self, like_ntype='storing'):
        """
        returns df with only the specified notification type (ntype)
        :param like_ntype: a term which looks like a known ntype.
        :return:
        """
        # Todo: functie omschrijven wanneer staging_file word weg gewerkt
        ntype = self._get_ntype(like_ntype=like_ntype)
        return self.staging_file_data[self.staging_file_data['type melding (Storing/Incident/Preventief/Onterecht)'] == ntype]

    """
    MAXIMO MODULES
    """
    def get_maximo_export(self, query=None):
        if query is None and self._maximo.query is None:
            raise ValueError("You're trying to make a request without a query. Set a query before making a request.")

        self._maximo.get_response_data(query)  # sets self.response_data
        return "Done."

    def save_maximo_export(self):
        self.filename_saved_response_data = self._maximo._default_file_name  # access to protected member
        # recursive function that keeps calling itself until an error occurs or the file is saved
        self._maximo.save_response_data(filename=self.filename_saved_response_data)

    """
    STAGING FILE MODULES
    """
    def build_staging_file(self, maximo_export_data_filename):
        sfb = StagingFileBuilder(maximo_export_data_filename=maximo_export_data_filename)
        sfb.build_staging_file()
        self.staging_file_name = sfb.export_file_name

    def read_staging_file(self, filename):
        self.staging_file_path = "..\\staging file\\" + filename
        self.staging_file_data = pd.read_excel(self.staging_file_path)

    def split_staging_file(self):
        self.meldingen = self.staging_file_data
        self.storingen = self._isolate_notification_type(like_ntype='storingen')
        return "Data available through the use of StoringsAnalyse.meldingen and StoringsAnalyse.storingen"

    """
    OTHER
    """
    def make_frequency_table(self, di_series):
        freq_table = {}
        for index, value in di_series.iteritems():
            di_num = self._isolate_di_number(index)
            if di_num in freq_table:
                freq_table[di_num] += value
            else:
                freq_table[di_num] = value
        return self._order_frequency_table(freq_table)
