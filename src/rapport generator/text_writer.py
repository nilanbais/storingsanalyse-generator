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

    """
    Managing modules -- Modules that fulfill some specific general task
    """
    def _return_ntype_objects(self, ntype: str) -> Tuple[DataFrame, DataFrame]:
        if ntype.lower() == 'meldingen':
            staging_data_ntype = self.meldingen
            meta_data_ntype = self.metadata.meldingen()
        elif ntype.lower() == 'storingen':
            staging_data_ntype = self.storingen
            meta_data_ntype = self.metadata.storingen()
        else:
            raise ValueError("Please parse 'meldingen' or 'storingen' as ntype.")

        return staging_data_ntype, meta_data_ntype

    @staticmethod
    def _return_poo_type_string(poo_type: str) -> str:
        if poo_type.lower() == 'probleem':
            poo_string = poo_type.lower() + ' code'
        elif poo_type.lower() == 'oorzaak':
            poo_string = poo_type.lower() + ' code'
        elif poo_type.lower() == 'oplossing':
            poo_string = poo_type.lower() + ' code'
        else:
            raise ValueError("Please parse 'probleem', 'oorzaak' or 'oplossing' as poo_type.")

        return poo_string

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

        staging_data_ntype, meta_data_ntype = self._return_ntype_objects(ntype=ntype)

        # Data voor in tekst ophalen
        ntype_per_maand = self.staging_file_data['month_number'].value_counts()

        gemiddelde_per_maand = sum(ntype_per_maand) / len(ntype_per_maand)

        max_ntype_maand = self.get_min_max_months(ntype_per_maand.to_dict(), min_max='max')
        min_ntype_maand = self.get_min_max_months(ntype_per_maand.to_dict(), min_max='min')

        # todo: excluse year aanpassen zodat het dynamisch is en niet gewoon '2020'
        maanden = self.metadata.get_month_list(exclude_year='2020')
        maandelijks_gemiddelde = self.metadata.avg_monthly(dictionary=meta_data_ntype, exclude_keys=maanden)

        kwartaal_gemiddelde = self.metadata.avg_quarterly(dictionary=meta_data_ntype)

        data_dict = {"ntype": ntype.lower(),
                     "totaal_aantal": len(staging_data_ntype),
                     "gemiddelde_per_maand": gemiddelde_per_maand,
                     "max_ntype_maand": max_ntype_maand,
                     "min_ntype_maand": min_ntype_maand,
                     "maandelijks_gemiddelde": maandelijks_gemiddelde,
                     "kwartaal_gemiddelde": kwartaal_gemiddelde}

        return data_dict

    def build_text_aantal_per_maand(self, input_data_dict: dict) -> str:
        text = f"""
        Om te kunnen bepalen of een trend waarneembaar is in het aantal meldingen per 
        maand, wordt als onderdeel van deze rapportage een grafiek toegevoegd. Zie 
        bijlage: “Aantal {input_data_dict["ntype"]} per maand”.

        Uit de grafiek valt het volgende te constateren:

        • Het totaal aantal {input_data_dict["ntype"]} in {self.quarter} {self.year} : {input_data_dict["totaal_aantal_meldingen"]} 

        • Het gemiddelde aantal {input_data_dict["ntype"]} per maand : {input_data_dict["gemiddelde_per_maand"]}

        • Hoogste aantal {input_data_dict["ntype"]} in de maand{'en' if len(input_data_dict["max_meldingen_maand"]) > 1 else ''} {', '.join(input_data_dict["max_meldingen_maand"])}: {max(input_data_dict["meldingen_per_maand"])}

        • Laagste aantal {input_data_dict["ntype"]} in de maand{'en' if len(input_data_dict["min_meldingen_maand"]) > 1 else ''} {', '.join(input_data_dict["min_meldingen_maand"])}: {min(input_data_dict["meldingen_per_maand"])}

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
        staging_data_ntype, meta_data_ntype = self._return_ntype_objects(ntype=ntype)

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

        staging_data_ntype, meta_data_ntype = self._return_ntype_objects(ntype=ntype)

        # unieke types vastlegen
        unique_types = list(staging_data_ntype.loc[:, 'sbs'].unique())

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
        staging_data_ntype, meta_data_ntype = self._return_ntype_objects(ntype='meldingen')
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

    def get_poo(self, poo_type: str, ) -> dict:
        """

        :param poo_type:
        :return:
        """
        # todo: build a module to update the meta with the staging file poo data. this action gets easier when only
        #  needing to acces poo_from_meta
        poo_type_count = self.meldingen[self._return_poo_type_string(poo_type)]

        poo_beschrijving = self.metadata.contract_info()['POO_codes']


        data_dict = {}
        return data_dict

    """
    Chapter - Assets met de meeste meldingen
        Paragraph - Algemeen
        Paragraph - Uitwerking meldingen
        Paragraph - Conclusie
    """
