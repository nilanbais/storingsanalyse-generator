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

from matplotlib.backends.backend_pdf import PdfPages

from stagingfile_class import StagingFileBuilder
from metadata_storingsanalyse import MetadataStoringsAnalyse
from query_maximo_database import QueryMaximoDatabase
from prepnplot import PrepNPlot

from pandas import DataFrame
from matplotlib.figure import Figure
from typing import Tuple, Optional, Union, List
from datetime import datetime, timedelta
from calendar import monthrange


# Todo: documentatie schrijven voor class
# Todo: Kijken hoe het type rapport (kwartaal of jaar) ingebouwd moet worden (wss als extra parameter bij aanmaken \
#  instance o.i.d.)
class StoringsAnalyse(PrepNPlot):

    # Class variables (callable by using class_name.var_name)
    _ld_map_path = "..\\..\\res\\location_description_map.json"  # location_description_map

    # todo aanpassen in documentatie
    def __init__(self, project: str, api_key: str, rapport_type: str, quarter: str, year: str, path_to_staging_file: str) -> None:
        # PrepNPlot Parameters
        PrepNPlot.__init__(self)

        # Metadata Parameters
        self.metadata = MetadataStoringsAnalyse(project)

        # Maximo Parameters
        self._maximo = QueryMaximoDatabase(api_key)
        self.response_data = self._maximo.response_data  # is set by get_maximo_export, default = None
        self.filename_saved_response_data = None

        # Staging File Parameters
        self.staging_file_name = None  # set by build_staging_file
        self.staging_file_path = path_to_staging_file
        self.staging_file_data = self.read_staging_file()

        self.meldingen = None  # set by split_staging_file
        self.storingen = None  # set by split_staging_file
        self.sbs_patch(project=project)
        self.split_staging_file()

        # General parameters
        # todo: aanpassen zodat geen df maar een dict o.i.d. wordt gebruikt als dtype van de attribute
        self._ld_map = self._read_ld_map()  # df with the mapped location and description

        self.project = project
        self.project_start_date = self.metadata.startdate()

        self.quarter = quarter
        self.year = year
        self.prev_quarter = self.quarter_sequence.get_prev_val(self.quarter)
        self.prev_year = str(int(self.year) - 1)

        self.metadata._quarter = quarter
        self.metadata._year = year

        self.analysis_time_range = self.get_time_range()
        self.analysis_start_date = self.analysis_time_range[0]
        self.analysis_end_date = self.analysis_time_range[-1]

        # Document parameters
        self.rapport_type = rapport_type
        self.graphs = []

        self.metadata.update_meta(staging_file_data=self.staging_file_data)

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
        description = [self._ld_map.loc[str(index), 'description']
                       for index in range(self._ld_map.shape[0])
                       if sbs_lbs == self._ld_map.loc[str(index), 'location']]
        return description[0] if len(description) > 0 else [""][0]  # To cover empty rows

    @staticmethod
    def _isolate_di_number(asset_num_string: str) -> str:
        return asset_num_string.split('-')[0]

    # todo: toevoegen aan documentatie
    def return_ntype_staging_file_object(self, ntype: str) -> DataFrame:
        if ntype.lower() == 'meldingen':
            staging_data_ntype = self.meldingen
        elif ntype.lower() == 'storingen':
            staging_data_ntype = self.storingen
        elif ntype.lower() == 'onterecht':
            staging_data_ntype = self._isolate_notification_type(like_ntype='onterecht').copy()
        elif ntype.lower() == 'preventief':
            staging_data_ntype = self._isolate_notification_type(like_ntype='preventief').copy()
        elif ntype.lower() == 'incident':
            staging_data_ntype = self._isolate_notification_type(like_ntype='incident').copy()
        else:
            raise ValueError("Please parse 'meldingen' or 'storingen' as ntype.")
        return staging_data_ntype

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

    @staticmethod
    def number_of_days_in_month(month, year):
        return monthrange(year=year, month=month)[-1]  # monthrange returns (first day of month, number of days in month)

    def get_time_range(self):
        months = sorted(list(PrepNPlot._quarters.__getitem__(self.quarter)))
        time_delta_days = sum([self.number_of_days_in_month(month=int(month), year=int(self.year)) for month in months])
        start_date = datetime(year=int(self.year), month=int(months[0]), day=1)  # always start a first of the month
        end_date = start_date + timedelta(days=(time_delta_days - 1))  # timedelta is UP UNTIL the first day of next Q, - 1 days to get last day of current Q
        return [start_date, end_date]

    # todo: toevoegen aan documentatie
    """
    Patch modules -- Modules that make adjustments that are easier/faster to change in a patch than to solve in source
    """
    def sbs_patch(self, project: str) -> None:
        """
        Patch for the different notation of the sbs numbers.
        :param project:
        :return:
        """
        if project.lower() in "coentunnel-tracé":
            new_data = []
            for sbs in self.staging_file_data['sbs']:
                new_sbs = str(sbs).split('-')[0]  # change '45-10' -> '45'
                new_sbs = '0' if new_sbs == '00' else new_sbs  # change '00' -> '0'
                new_data.append(new_sbs)

            self.staging_file_data['sbs'] = new_data

    """
    Database modules -- Modules that focus on the interaction with the database (all _maximo related moludes).
    """
    # todo: aanpassen in documentatie
    def query_maximo_database(self, site_id: str, work_type: str = "COR") -> str:  # todo: naam veranderen naar query_maximo_database (ook in documentatie)
        query = self.build_query(site_id, self.analysis_time_range, work_type)
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

    def read_staging_file(self) -> DataFrame:
        return pd.read_excel(self.staging_file_path)

    # Todo: output type aanpassen in documentatie
    def split_staging_file(self) -> None:
        self.meldingen = self.staging_file_data
        self.storingen = self._isolate_notification_type(like_ntype='storingen')

    @staticmethod
    def _get_ntype(like_ntype: str) -> str:
        if like_ntype.lower() in {'m', 'melding', 'meldingen'}:
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
        result = self.staging_file_data[self.staging_file_data['type melding (Storing/Incident/Preventief/Onterecht)'] == ntype]
        return result

    """
    Metadata modules -- Modules that focus on handling (preperation and transformation) of the input data.
    """

    """
    Prep and Plot modules -- Modules that focus on the preperation, transformation and plotting.
    """
    def _add_graph_for_export(self, figure: Figure) -> None:
        self.graphs.append(figure)

    def plot(self, input_data: List[list], plot_type: str, category_labels: list, bin_labels: list, show_plot: bool = False) -> None:
        fig = PrepNPlot.plot(self, input_data, plot_type, category_labels, bin_labels)
        self._add_graph_for_export(fig)

    def plot_summary(self, x_labels: list, data: list, show_plot: bool = False) -> None:
        fig = PrepNPlot.plot_summary(x_labels, data)  # plot_summary is static in PrepNPlot so no 'self' here
        self._add_graph_for_export(fig)

    def export_graphs(self, filename: str) -> None:
        pdfp = PdfPages(filename)
        for graph in self.graphs:
            pdfp.savefig(graph)
        pdfp.close()
