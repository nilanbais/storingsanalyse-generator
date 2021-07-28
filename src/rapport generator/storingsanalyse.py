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
from prepnplot import PrepNPlot

from typing import Dict

# Todo: documentatie schrijven voor class
# Todo: Kijken hoe het type rapport (kwartaal of jaar) ingebouwd moet worden (wss als extra parameter bij aanmaken \
#  instance o.i.d.)
class StoringsAnalyse(PrepNPlot):

    # Class variables (callable by using class_name.var_name)
    _ld_map_path = "..\\..\\res\\location_description_map.json"  # location_description_map

    def __init__(self, project, api_key, object_structure) -> None:
        PrepNPlot.__init__(self)

        self.metadata = MetadataStoringsAnalyse(project)

        self._maximo = QueryMaximoDatabase(api_key, object_structure)
        self.response_data = self._maximo.response_data  # is set by get_maximo_export, default = None
        self.filename_saved_response_data = None

        self.staging_file_name = None  # set by build_staging_file
        self.staging_file_path = None  # set by get_staging_file
        self.staging_file_data = None  # set by get_staging_file
        self.meldingen = None  # set by split_staging_file
        self.storingen = None  # set by split_staging_file

        # todo: aanpassen zodat geen df maar een dict o.i.d. wordt gebruikt als dtype van de attribute
        self._ld_map = self._read_ld_map()  # df with the mapped location and description

        self.project = self.metadata.project()
        self.start_date = self.metadata.startdate()

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

    def _get_breakdown_description(self, sbs_lbs):
        description = [self._ld_map.loc[str(index), 'description']
                       for index in range(self._ld_map.shape[0])
                       if sbs_lbs == self._ld_map.loc[str(index), 'location']]
        return description if len(description) > 0 else [""]  # To cover empty rows

    def get_maximo_export(self, query=None):  # todo: naam veranderen naar query_maximo_database (ook in documentatie)
        if query is None and self._maximo.query is None:
            raise ValueError("You're trying to make a request without a query. Set a query before making a request.")

        self._maximo.get_response_data(query)  # sets self.response_data
        return "Done."
    
    def save_maximo_export(self):  # todo: naam veranderen naar save_maximo_response_data (ook in documentatie)
        self.filename_saved_response_data = self._maximo._default_file_name  # access to protected member
        # recursive function that keeps calling itself until an error occurs or the file is saved
        self._maximo.save_response_data(filename=self.filename_saved_response_data)

    @staticmethod
    def _month_num_to_name(month_num: int or list) -> str:
        maand_dict = {"1": "Januari", "2": "Februari", "3": "Maart", "4": "April", "5": "Mei", "6": "Juni", "7": "Juli",
                      "8": "Augustus", "9": "September", "10": "Oktober", "11": "November", "12": "December", }
        if isinstance(month_num, list):
            maand = [maand_dict[str(num)] for num in month_num for key in maand_dict.keys() if str(num) == key]
            return maand[0]
        elif isinstance(month_num, int):
            return maand_dict[str(month_num)]

    @staticmethod
    def _isolate_di_number(asset_num_string):
        return asset_num_string.split('-')[0]

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

    def totaal_aantal_x_export(self, x='meldingen'):
        if x == 'storingen':
            return len(self.storingen)
        return len(self.meldingen)

    def x_per_maand(self, x='meldingen'):
        if x == 'storingen':
            return self.storingen['month_number'].value_counts()
        return self.meldingen['month_number'].value_counts()

    # def storingen_per_maand(self):
    #     return self.x_per_maand(x='storingen')

    def avg_x_per_maand(self, x='meldingen'):
        return sum(self.x_per_maand(x=x)) / len(self.x_per_maand(x=x))

    def maand_max_min_x(self, min_max='max', x='meldingen'):
        if min_max == 'min':
            num_maand_meeste_meldingen = [self.x_per_maand(x=x).index[self.x_per_maand(x=x) == min(self.x_per_maand(x=x))][0]]
        else:
            num_maand_meeste_meldingen = [self.x_per_maand(x=x).index[self.x_per_maand(x=x) == max(self.x_per_maand(x=x))][0]]
        maand = self._month_num_to_name(month_num=num_maand_meeste_meldingen)
        return maand[0] if len(maand) == 1 else maand

    # todo: meldingen_2019 in jn vertalen naar module
    def x_voorgaande_jaar(self):
        pass

    def plot_ntype_per_maand(self, ntype='meldingen'):
        pass
