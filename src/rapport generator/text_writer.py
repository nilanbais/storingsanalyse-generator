"""
Class voor het genereren van de tekst voor de verschillende projecten.

Hoe dit precies wordt opgebouwd is work-in-progress -> het kan dat er per project een specifieke class geschreven
moet worden, maar dat deze gebruik maken van één overkoepelende class die de meest generalistische functies bevat.

Voor de Coentunnel wordt begonnen met het opbouwen van een class die specifiek voor de Coentunnel is. In de loop
van dit process wordt er gekeken naar de mogelijkheden om het eerder beschreven idee te realiseren
"""
from storingsanalyse_v2 import StoringsAnalyse
from typing import Tuple
from pandas import DataFrame


# todo: toevoegen aan documentatie
class DocumentGeneratorCoentunnel(StoringsAnalyse):

    def __init__(self, project: str, api_key: str, rapport_type: str, quarter: str, year: str, path_to_staging_file: str) -> None:
        StoringsAnalyse.__init__(self, project, api_key, rapport_type, quarter, year, path_to_staging_file)
        self.newline = "\n"
        self.tab = "\t"
        print(f'self.staging from dg\n{self.staging_file_data}')

    """
    Managing modules -- Modules that fulfill some specific general task
    """
    def _return_ntype_staging_file_object(self, ntype: str) -> DataFrame:
        if ntype.lower() == 'meldingen':
            staging_data_ntype = self.meldingen
        elif ntype.lower() == 'storingen':
            print(self.storingen)
            staging_data_ntype = self.storingen
        else:
            raise ValueError("Please parse 'meldingen' or 'storingen' as ntype.")
        return staging_data_ntype

    def __aantal_per_maand(self, input_data: DataFrame, ntype: str) -> dict:
        meta_data_ntype = self.metadata.return_ntype_meta_object(ntype=ntype)

        # Data voor in tekst ophalen
        ntype_per_maand = input_data['month_number'].value_counts()

        gemiddelde_per_maand = sum(ntype_per_maand) / len(ntype_per_maand)

        max_ntype_maand = self.get_min_max_months(ntype_per_maand.to_dict(), min_max='max')
        min_ntype_maand = self.get_min_max_months(ntype_per_maand.to_dict(), min_max='min')

        # todo: excluse year aanpassen zodat het dynamisch is en niet gewoon '2020'
        maanden = self.metadata.get_month_list(exclude_year='2020')
        maandelijks_gemiddelde = self.metadata.avg_monthly(dictionary=meta_data_ntype, exclude_keys=maanden)

        kwartaal_gemiddelde = self.metadata.avg_quarterly(dictionary=meta_data_ntype)

        data_dict = {"ntype": ntype.lower(),
                     "totaal_aantal": len(input_data),
                     "ntype_count_per_maand": ntype_per_maand,
                     "gemiddelde_per_maand": gemiddelde_per_maand,  # just this quarter
                     "max_ntype_maand": max_ntype_maand,
                     "min_ntype_maand": min_ntype_maand,
                     "maandelijks_gemiddelde": maandelijks_gemiddelde,  # over the whole project
                     "kwartaal_gemiddelde": kwartaal_gemiddelde}

        return data_dict
    """
    Chapter - Analyse
        Paragraph - Aantal meldingen
            Subsection - Aantal meldingen per maand
            Subsection - Aantal meldingen per subsysteem
        Paragraph - Aantal storingen
            Subsection - Aantal storingen per maand
            Subsection - Aantal storingen per subsysteem
    """
    def get_aantal_per_maand(self, ntype: str) -> dict:
        staging_data_ntype = self._return_ntype_staging_file_object(ntype=ntype)
        return self.__aantal_per_maand(input_data=staging_data_ntype, ntype=ntype)

    def build_text_aantal_per_maand(self, input_data_dict: dict) -> str:
        text = f"""
        Om te kunnen bepalen of een trend waarneembaar is in het aantal meldingen per 
        maand, wordt als onderdeel van deze rapportage een grafiek toegevoegd. Zie 
        bijlage: “Aantal {input_data_dict["ntype"]} per maand”.

        Uit de grafiek valt het volgende te constateren:

        • Het totaal aantal {input_data_dict["ntype"]} in {self.quarter} {self.year} : {input_data_dict["totaal_aantal"]} 

        • Het gemiddelde aantal {input_data_dict["ntype"]} per maand : {input_data_dict["gemiddelde_per_maand"]}

        • Hoogste aantal {input_data_dict["ntype"]} in de maand{'en' if len(input_data_dict["max_ntype_maand"]) > 1 else ''} {', '.join(input_data_dict["max_ntype_maand"])}: {max(input_data_dict["ntype_count_per_maand"])}

        • Laagste aantal {input_data_dict["ntype"]} in de maand{'en' if len(input_data_dict["min_ntype_maand"]) > 1 else ''} {', '.join(input_data_dict["min_ntype_maand"])}: {min(input_data_dict["ntype_count_per_maand"])}

        • Het gemiddelde aantal {input_data_dict["ntype"]} per maand vanaf **{self.project_start_date}**: **{input_data_dict["maandelijks_gemiddelde"]}**

        • Het gemiddelde aantal {input_data_dict["ntype"]} per kwartaal vanaf **{self.project_start_date}**: **{input_data_dict["kwartaal_gemiddelde"]}**
        """
        return text

    def get_quarter_comparison(self, ntype: str) -> dict:
        """
        The subsections 'aantal ntype per maand' contain a comparison of the current quarter with the previous
        quarter, and a comparison of the current quarter with the selfme quarter of the previous year.
        :return:
        """
        staging_data_ntype = self._return_ntype_staging_file_object(ntype=ntype)
        meta_data_ntype = self.metadata.return_ntype_meta_object(ntype=ntype)

        # Aantal ntype in voorgaande q
        monthlist = self.metadata.get_keys(dictionary=meta_data_ntype, containing_quarter=[self.prev_quarter],
                                           containing_year=[self.prev_year])
        ntype_gefilterd = self.metadata.filter_dictionary_keys(dictionary=meta_data_ntype, keys=monthlist)
        totaal_ntype_voorgaand_kwartaal = self.metadata.sum_values(ntype_gefilterd)

        # Aantal ntype in zelfde q voorgaand jaar
        monthlist = self.metadata.get_keys(dictionary=meta_data_ntype, containing_quarter=[self.quarter],
                                           containing_year=[self.prev_year])
        ntype_gefilterd = self.metadata.filter_dictionary_keys(dictionary=meta_data_ntype, keys=monthlist)
        totaal_ntype_zelfde_kwartaal = self.metadata.sum_values(ntype_gefilterd)

        data_dict = {"ntype": ntype.lower(),
                     "totaal_aantal": len(staging_data_ntype),
                     "totaal_ntype_zelfde_kwartaal": totaal_ntype_zelfde_kwartaal,
                     "totaal_ntype_voorgaande_kwartaal": totaal_ntype_voorgaand_kwartaal}
        return data_dict

    def build_quarter_comparison(self, input_data_dict: dict) -> str:
        text = f"""
        In {self.quarter} {self.prev_year} waren in totaal {input_data_dict["totaal_ntype_zelfde_kwartaal"]} {input_data_dict["ntype"]} gemaakt. In {self.quarter} {self.year} zijn er {input_data_dict["totaal_aantal"] - input_data_dict["totaal_ntype_zelfde_kwartaal"]} {input_data_dict["ntype"]} 
        meer t.o.v. {self.quarter} {self.prev_year}. 

        In **{self.prev_quarter} {self.year} waren in totaal {input_data_dict["totaal_ntype_voorgaande_kwartaal"]} {input_data_dict["ntype"]} gemaakt. In {self.quarter} {self.year} zijn er {input_data_dict["totaal_aantal"] - input_data_dict["totaal_ntype_voorgaande_kwartaal"]} {input_data_dict["ntype"]} 
        meer t.o.v. **{self.prev_quarter}** **{self.year}**. 
        """
        return text

    def get_aantal_per_subsysteem(self, ntype: str, threshold: int) -> dict:

        staging_data_ntype = self._return_ntype_staging_file_object(ntype=ntype)

        # unieke types vastlegen
        # unique_types = list(staging_data_ntype.loc[:, 'sbs'].unique())

        sbs_count = staging_data_ntype.loc[:, 'sbs'].value_counts()

        # sbs nummers die verwerkt moeten worden
        sbs_to_process = [x for x in sbs_count.index if sbs_count.at[x] >= threshold]

        # lijst met rijen die verwerkt moeten worden
        rows_to_process = list()
        for sbs in sbs_to_process:
            ntype_per_sbs = sbs_count[sbs]
            percentage_ntype = round((ntype_per_sbs / sum(sbs_count)) * 100, 2)
            line = f"{self._get_breakdown_description(sbs)}{self.tab}- {ntype_per_sbs} meldingen ({percentage_ntype}% van het totale aantal meldingen)"
            rows_to_process.append(line)

        # notification type
        ntypes = list(staging_data_ntype.loc[:, 'type melding (Storing/Incident/Preventief/Onterecht)'].unique())
        print(ntypes)

        ntype_count = staging_data_ntype.loc[:, 'type melding (Storing/Incident/Preventief/Onterecht)'].value_counts()
        print(ntype_count)

        lines_to_process = list()
        for n in ntypes:
            line = f"{ntype_count[n]} meldingen zijn gecategoriseerd als {n}."
            lines_to_process.append(line)

        data_dict = {"ntype": ntype.lower(),
                     "threshold": threshold,
                     "totaal_aantal": len(staging_data_ntype),
                     "sbs_count": sbs_count,
                     "sbs_to_process": sbs_to_process,
                     "rows_to_process": rows_to_process,
                     "lines_to_process": lines_to_process}
        return data_dict

    def build_text_aantal_per_subsysteem(self, input_data_dict: dict) -> str:
        text = f"""
        Er wordt en Pareto analyse gemaakt van het totaal aantal meldingen per subsysteem. Deze is toegevoegd als bijlage. 

        Uit de pareto blijkt dat in **{self.quarter}** **{self.prev_year}** een totaal van **{input_data_dict["totaal_aantal"]}** meldingen zijn gemeld, intern 
        dan wel extern. Voor het overzicht zijn de meldingen bekeken met **{input_data_dict["threshold"]}** of meer 
        meldingen. Dit is de top **{len(input_data_dict["sbs_to_process"])}** en heeft een totaal van **{sum(input_data_dict["sbs_count"][input_data_dict["sbs_to_process"]])}** meldingen van de in totaal 
        **{input_data_dict["totaal_aantal"]}** (dit is **{round((sum(input_data_dict["sbs_count"][input_data_dict["sbs_to_process"]]) / input_data_dict["totaal_aantal"]) * 100, 2)}**% van het totaal). 
        Hieronder staan de deelinstallatie**{'s' if len(input_data_dict["sbs_to_process"]) > 1 else ''}**:


        {''.join((self.newline + '**-' + self.tab + line + '**' + self.newline for line in input_data_dict["rows_to_process"]))}


        De **{input_data_dict["totaal_aantal"]}** van **{self.quarter}** **{self.year}** zijn als volgt onder te verdelen:

        {''.join((self.newline + '**-' + self.tab + ntype_line + '**' + self.newline for ntype_line in input_data_dict["lines_to_process"]))}
        """
        return text

    """
    Chapter - Conclusie/Aanbeveling
        Paragraph - Algemeen
            Subsection - Probleem
            Subsection - Oorzaak
            Subsection - Oplossing
        Paragraph - Storingen per deelinstallatie
            Subsection - [subsectie voor elk uitgewerkte subsysteem. Title = subsystem_name]
    """
    def build_algemeen_intro(self) -> str:
        staging_data_ntype = self._return_ntype_staging_file_object(ntype='meldingen')
        sbs_count = staging_data_ntype.loc[:, 'sbs'].value_counts(dropna=False)

        text = f"""
        Er heeft een analyse van de storingen plaatsgevonden. Uit deze analyse is niet 
        naar voren gekomen dat verbeteren aan het onderhoudsplan en/of procedures en/of 
        hardware noodzakelijk zijn om het faalgedrag te verbeteren. 

        Alle meldingen moeten aan een asset / sub niveau van een DI worden gekoppeld. 
        Zodat altijd is te herleiden wat precies is gefaald. Aan alle meldingen is een DI 
        gekoppeld. Aan **{max(sbs_count[sbs_count.index.isnull()].values) if len(sbs_count[sbs_count.index.isnull()]) != 0 else 0}** werkorders zit geen sbs nummer gekoppeld. (zie besluit 5). 

        De meldingen zijn gekoppeld aan een probleem, oorzaak en oplossing. 

        Vanaf 1 september 2018 heeft een update plaats gevonden van het 
        onderhoudsmanagementsysteem. Bij deze update is het invullen van probleem, 
        oorzaak en oplossing toegevoegd in het systeem. Vanaf Q4 2018 zal dit ook 
        worden meegenomen in de analyse. In de volgende paragrafen staat de uitwerking 
        hiervan. Daarbij zie je het aantal van het huidige jaar, het totaal aantal en het 
        gemiddelde per Q vanaf Q4 2018.
        """
        return text

    def get_poo_table_data(self, poo_type: str) -> dict:
        """

        :param poo_type:
        :return:
        """
        # todo: build a module to update the meta with the staging file poo data. this action gets easier when only
        #  needing to acces poo_from_meta
        poo_type_string = self.metadata.return_poo_type_string(poo_type)

        poo_type_count = self.meldingen[poo_type_string].value_counts(dropna=False).to_dict()

        meta_poo_type = self.metadata.poo_data()[poo_type_string.split(' ')[0]]

        poo_type_avg_table = self.metadata.poo_avg_table(poo_dictionary=meta_poo_type, poo_type=poo_type)

        poo_beschrijvingen = self.metadata.contract_info()['POO_codes']

        data_dict = dict()
        for code in self.metadata.return_poo_code_list(poo_type):
            code_counts = list()

            for quarter in meta_poo_type.keys():
                if code in meta_poo_type[quarter].keys():
                    code_counts.append(self.metadata.sum_values(dictionary=meta_poo_type[quarter], keys=[code]))
                else:
                    code_counts.append(0)

            totaal = sum(code_counts)
            if code not in poo_type_count.keys():
                line = ''.join((self.newline + '|' + code + '|' + poo_beschrijvingen[code] + '|' + str(0) + '|' + str(totaal) + '|' + str(poo_type_avg_table[code]) + '|'))
                data_dict[code] = line
                continue

            line = ''.join((self.newline + '|' + code + '|' + poo_beschrijvingen[code] + '|' + str(poo_type_count[code]) + '|' + str(totaal + poo_type_count[code]) + '|' + str(poo_type_avg_table[code]) + '|'))
            data_dict[code] = line

        return data_dict

    @staticmethod
    def build_poo_table(input_data_dict: dict) -> str:
        text = """|Probleem|Beschrijving|Aantal|Totaal|Gemiddelde|
        |--------|------------|------|------|----------|""" + ''.join((input_data_dict[code] for code in input_data_dict.keys()))
        return text

    def get_aantal_per_subsysteem_per_maand(self, threshold: int, ntype: str = 'meldingen') -> dict:
        """

        :param threshold:
        :param ntype: default value = 'meldingen' because the standard analysis is preformed on the ntype 'meldingen'
        :return:
        """
        staging_data_ntype = self._return_ntype_staging_file_object(ntype=ntype)
        sf_data_groupby_sbs = staging_data_ntype.groupby('sbs')

        _group_data_to_print = dict()
        for group in sf_data_groupby_sbs.groups:
            group_data = sf_data_groupby_sbs.get_group(group)

            if len(group_data.index) < threshold:
                continue

            _group_data_to_print[group] = self.__aantal_per_maand(input_data=group_data, ntype=ntype)

        sorted_keys = sorted(_group_data_to_print, key=lambda item: _group_data_to_print[item]['totaal_aantal'], reverse=True)
        group_data_dict = {key: _group_data_to_print[key] for key in sorted_keys}
        return group_data_dict

    def build_aantal_per_subsysteem_per_maand(self, input_data_dict: dict) -> str:
        """

        :param input_data_dict: a dict of dicts for each subsystem a subdict
        :return:
        """
        text = """"""
        for sub_system in input_data_dict.keys():
            sub_system_data = input_data_dict[sub_system]
            print(f'subsystem {sub_system}\n{sub_system_data}')
            sub_system_name = self._get_breakdown_description(sbs_lbs=sub_system)
            print(sub_system_name, type(sub_system_name))
            text = text + '# ' + str(sub_system) + sub_system_name + self.newline + self.build_text_aantal_per_maand(input_data_dict=sub_system_data)

        return text

    """
    Chapter - Assets met de meeste meldingen
        Paragraph - Algemeen
        Paragraph - Uitwerking meldingen
        Paragraph - Conclusie
    """

if __name__ == '__main__':
    dg = DocumentGeneratorCoentunnel(project="Coentunnel-tracé",
                                    rapport_type="Kwartaalrapportage",
                                    quarter="Q2",
                                    year="2021",
                                    api_key='bWF4YWRtaW46R21iQ1dlbkQyMDE5',
                                    path_to_staging_file='..\\staging file\\validating_input_data.xlsx')
