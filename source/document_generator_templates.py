"""
Class voor het genereren van documenten met behulp van templates.

"""
from storingsanalyse import StoringsAnalyse
import docxtpl


class DocumentGenerator:

    def __init__(self, project: str, api_key: str, rapport_type: str, quarter: str, year: str, staging_file_name: str = None) -> None:
        self.sa = StoringsAnalyse(project, api_key, rapport_type, quarter, year, staging_file_name)

        self._default_export_file_name = f"TEST_{self.sa.quarter}_{self.sa.year}_storingsanalyse_tekst.docx"
        self._default_export_file_name_appendix = f"TEST_{self.sa.quarter}_{self.sa.year}_storingsanalyse_bijlage.pdf"

        self.template_folder = "resources/document_templates"
        self.rendered_document_folder = "resources/temp"
        self.default_export_location = "documents/generated_documents"

    def create_rendered_document(self, data_package: dict, template_file: str) -> None:
        doc = docxtpl.DocxTemplate(template_file)
        doc.render(data_package)
        doc.save("{0}/render_{1}".format(self.rendered_document_folder, template_file))

    def get_data_h3(self, ntype: str, threshold: int) -> dict:

        # Set input data to variable
        staging_file_data = self.sa.return_ntype_staging_file_object(ntype=ntype)
        meta_data_ntype = self.sa.metadata.return_ntype_meta_object(ntype=ntype)

        total_notifications = len(staging_file_data)

        staging_file_data_groupby_month = staging_file_data['month_number'].value_counts()

        monthly_avg_current_quarter = sum(staging_file_data_groupby_month) / len(staging_file_data_groupby_month)

        # gives the min and max number of notifications
        max_monthly_notifications = max(staging_file_data_groupby_month)
        min_monthly_notifications = min(staging_file_data_groupby_month)

        # gives the month names of those with min and max notifications
        month_max_notifications = self.sa.get_min_max_months(staging_file_data_groupby_month.to_dict(), min_max='max')
        month_min_notifications = self.sa.get_min_max_months(staging_file_data_groupby_month.to_dict(), min_max='min')

        # quarter comparisons
        monthlist = self.sa.metadata.get_keys(dictionary=meta_data_ntype, containing_quarter=[self.sa.quarter],
                                              containing_year=[self.sa.prev_year])
        ntype_gefilterd = self.sa.metadata.filter_dictionary_keys(dictionary=meta_data_ntype, keys=monthlist)
        total_notifications_prev_year = self.sa.metadata.sum_values(ntype_gefilterd)

        difference_curr_year_prev_year = total_notifications - total_notifications_prev_year

        # Aantal ntype in voorgaande q
        monthlist = self.sa.metadata.get_keys(dictionary=meta_data_ntype, containing_quarter=[self.sa.prev_quarter],
                                              containing_year=[self.sa.prev_year])
        ntype_gefilterd = self.sa.metadata.filter_dictionary_keys(dictionary=meta_data_ntype, keys=monthlist)
        total_notifications_prev_q = self.sa.metadata.sum_values(ntype_gefilterd)
        difference_curr_q_prev_q = 0

        sbs_count = staging_file_data.loc[:, 'sbs'].value_counts()
        sbs_numbers_to_process = [x for x in sbs_count.index if sbs_count.at[x] >= threshold]

        count_unique_sbs_numbers = len(sbs_numbers_to_process)
        notification_count_unique_sbs_numbers = sum(sbs_count[sbs_numbers_to_process])

        # percentage notifications unique sbs numbers against total notifications
        special_percentage = round((notification_count_unique_sbs_numbers / total_notifications) * 100, 2)

        staging_file_data_groupby_ntype = staging_file_data.loc[:, 'type melding (Storing/Incident/Preventief/Onterecht)'].value_counts()

        # counts per ntype
        count_storingen = staging_file_data_groupby_ntype['Storing']
        count_preventief = staging_file_data_groupby_ntype['Preventief']
        count_incident = staging_file_data_groupby_ntype['Incident']
        count_onterecht = staging_file_data_groupby_ntype['Onterecht']

        rows_to_process = []
        for sbs in sbs_numbers_to_process:
            count_notifications = sbs_count[sbs]
            sbs_name = self.sa.get_breakdown_description(sbs_lbs=sbs)
            row_percentage = round((count_notifications/sbs_count) * 100, 2)
            row = {"sbs_name": sbs_name,
                   "count_notifications": count_notifications,
                   "percentage": row_percentage}
            rows_to_process.append(row)

        data_package = {"ntype": ntype.lower(),
                        "q_current": self.sa.quarter,
                        "q_prev": self.sa.prev_quarter,
                        "year_current": self.sa.year,
                        "year_prev": self.sa.prev_year,
                        "threshold": threshold,
                        "total_notifications": total_notifications,
                        "month_name_highest": month_max_notifications,
                        "month_name_lowest": month_min_notifications,
                        "max_monthly_notifications": max_monthly_notifications,
                        "min_monthly_notifications": min_monthly_notifications,
                        "monthly_avg": monthly_avg_current_quarter,
                        "count_unique_sbs_numers": count_unique_sbs_numbers,
                        "notifications_unique_sbs_numbers": notification_count_unique_sbs_numbers,
                        "percentage_unique_sbs_numbers_to_total": special_percentage,
                        "count_storingen": count_storingen,
                        "count_preventief": count_preventief,
                        "count_incident": count_incident,
                        "count_onterecht": count_onterecht,
                        "total_notifications_prev_year": total_notifications_prev_year,
                        "difference_curr_year_prev_year": difference_curr_year_prev_year,
                        "total_notifications_prev_q": total_notifications_prev_q,
                        "difference_curr_q_prev_q": difference_curr_q_prev_q,
                        "rows_to_process": rows_to_process,
                        }

        return data_package
