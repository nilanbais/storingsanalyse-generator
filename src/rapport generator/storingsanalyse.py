"""
DEZE CLASS IS VEROUDERD. ER IS EEN NIEUWERE VERSIE ONTWIKKELD DIE NU WORDT ONDERHOUDEN.

DIT DOCUMENT WORDT NIET ONDERHOUDEN.

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

from matplotlib.backends.backend_pdf import PdfPages

from stagingfile_class import StagingFileBuilder
from metadata_storingsanalyse import MetadataStoringsAnalyse
from query_maximo_database import QueryMaximoDatabase
from prepnplot import PrepNPlot

from pandas import DataFrame
from matplotlib.figure import Figure
from typing import Tuple, Optional, Union, List
from datetime import datetime


# Todo: documentatie schrijven voor class
# Todo: Kijken hoe het type rapport (kwartaal of jaar) ingebouwd moet worden (wss als extra parameter bij aanmaken \
#  instance o.i.d.)
class StoringsAnalyse(PrepNPlot):

    # Class variables (callable by using class_name.var_name)
    _ld_map_path = "..\\..\\res\\location_description_map.json"  # location_description_map

    def __init__(self, project: str, api_key: str) -> None:
        PrepNPlot.__init__(self)

        self.metadata = MetadataStoringsAnalyse(project)

        self._maximo = QueryMaximoDatabase(api_key)
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

        self.graphs = []

    """
    Managing modules -- Modules that fulfill some specific general task
    """
    @staticmethod
    def _read_ld_map() -> DataFrame:
        """
        Module to load the data for the descriptions of the location breakdown structure numbers (LBS) and the system
        breakdown structure numbers (SBS).
        :return:
        """
        with open(os.path.relpath(StoringsAnalyse._ld_map_path), 'r') as file:
            description_data = json.load(file)
        return pd.DataFrame(description_data)

    def _get_breakdown_description(self, sbs_lbs: str) -> str:
        sbs_lbs = '00' if sbs_lbs == '0' else sbs_lbs  # patch for Coentunnel
        description = [self._ld_map.loc[str(index), 'description']
                       for index in range(self._ld_map.shape[0])
                       if sbs_lbs == self._ld_map.loc[str(index), 'location']]
        return description[0] if len(description) > 0 else [""]  # To cover empty rows

    @staticmethod
    def _isolate_di_number(asset_num_string: str) -> str:
        return asset_num_string.split('-')[0]

    # Todo: toevoegen aan documentatie
    def get_min_max_months(self, notifications_groupby_months: dict, min_max: str) -> list:
        """
        Returns a list with the names of the month(s) corresponding to the values based on the parameter min_max
        :param notifications_groupby_months:
        :param min_max:
        :return:
        """
        # Extrema = min or max (specified max_max input parameter)
        if min_max == 'max':
            extrema_notifications_month = [key for key, value in notifications_groupby_months.items()
                                           if value == max(notifications_groupby_months.values())]
        elif min_max == 'min':
            extrema_notifications_month = [key for key, value in notifications_groupby_months.items()
                                           if value == min(notifications_groupby_months.values())]
        else:
            raise ValueError("Please parse 'max' or 'min' as string for the max_min parameter.")

        return [self._month_num_to_name(n) for n in extrema_notifications_month]

    """
    Database modules -- Modules that focus on the interaction with the database (all _maximo related moludes).
    """
    def query_maximo_database(self, site_id: str, report_time: List[datetime], work_type: str = "COR") -> str:  # todo: naam veranderen naar query_maximo_database (ook in documentatie)
        query = self.build_query(site_id, report_time, work_type)
        self._maximo.get_response_data(query=query)  # sets self.response_data
        return "Query finished successfully."

    def save_maximo_data(self) -> None:  # todo: naam veranderen naar save_maximo_response_data (ook in documentatie)
        self.filename_saved_response_data = self._maximo._default_file_name  # access to protected member
        # recursive function that keeps calling itself until an error occurs or the file is saved
        self._maximo.save_response_data(filename=self.filename_saved_response_data)

    @staticmethod
    def build_query(site_id: str, report_time: List[datetime], work_type: str = "COR") -> str:
        """
        Returns the query string
        :param site_id:
        :param report_time:
        :param work_type:
        :return:
        """
        start_date, end_date = [datetime.strftime(dt, '%Y-%m-%d') for dt in report_time]
        query = f'sited="{site_id}" and worktype="{work_type}" and reportdate >= "{start_date}" and reportdate <= "{end_date}"'
        return query

    """
    StagingFile modules -- Modules that focus on the actions in relation to the Staging File.
    """
    def build_staging_file(self, maximo_export_data_filename: str) -> None:
        sfb = StagingFileBuilder(maximo_export_data_filename=maximo_export_data_filename)
        sfb.build_staging_file()
        self.staging_file_name = sfb.export_file_name

    def read_staging_file(self, filename: str) -> None:
        self.staging_file_path = "..\\staging file\\" + filename
        self.staging_file_data = pd.read_excel(self.staging_file_path)

    # Todo: output type aanpassen in documentatie
    def split_staging_file(self) -> None:
        self.meldingen = self.staging_file_data
        self.storingen = self._isolate_notification_type(like_ntype='storingen')

    def _get_ntype(self, like_ntype: str) -> str:
        if like_ntype is None:
            return self.staging_file_data
        elif like_ntype.lower() in {'m', 'melding', 'meldingen'}:
            return "Melding"
        elif like_ntype.lower() in {'s', 'storing', 'storingen'}:
            return "Storing"
        elif like_ntype.lower() in {'i', 'incident', 'incidenten'}:
            return "Incident"
        elif like_ntype.lower() in {'p', 'preventief'}:
            return "Preventief"
        elif like_ntype.lower() in {'o', 'onterecht'}:
            return "Onterecht"
        elif like_ntype.lower() in {"meldingen", "storing", "incident", "preventief", "onterecht"}:
            return like_ntype
        else:
            raise ValueError("Please select either \"Melding\", \"Storing\", \"Incident\", \"Preventief\", "
                             "\"Onterecht\" as like_ntype.")

    def _isolate_notification_type(self, like_ntype: str = 'storing') -> DataFrame:
        """
        returns df with only the specified notification type (ntype)
        :param like_ntype: a term which looks like a known ntype.
        :return:
        """
        # Todo: functie omschrijven wanneer staging_file word weg gewerkt
        ntype = self._get_ntype(like_ntype=like_ntype)
        return self.staging_file_data[self.staging_file_data['type melding (Storing/Incident/Preventief/Onterecht)'] == ntype]

    """
    Metadata modules -- Modules that focus on handling (preperation and transformation) of the input data.
    """

    """
    Prep and Plot modules -- Modules that focus on the preperation, transformation and plotting.
    """
    def _add_graph_for_export(self, figure: Figure) -> None:
        self.graphs.append(figure)

    def plot(self, input_data: List[list], plot_type: str, category_labels: list, bin_labels: list) -> None:
        fig = PrepNPlot.plot(self, input_data, plot_type, category_labels, bin_labels)
        self._add_graph_for_export(fig)

    def plot_summary(self, x_labels: list, data: list) -> None:
        fig = PrepNPlot.plot_summary(x_labels, data)  # plot_summary is static in PrepNPlot so no 'self' here
        self._add_graph_for_export(fig)

    def export_graphs(self, filename: str) -> None:
        pdfp = PdfPages(filename)
        for graph in self.graphs:
            pdfp.savefig(graph)
        pdfp.close()
