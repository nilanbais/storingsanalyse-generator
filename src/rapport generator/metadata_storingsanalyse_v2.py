"""
This script is for the development of the functions to use on the metadata.
Building some sort of layer on top op the standardized lay-out of the metadata makes working with the data in
a Jupyter Notebook easier and more organized.

The functions are written for a json metadata file generated by the metadata_file builder
{
    project: projectnaam,
    start_datum: dd-mm-yyy,
    contract_info: {
        tijdsregistratie: True,
        ...
    },
    meldingen: {
        f"{maand}_{jaar}": {
            DI_num: aantal meldingen,
            DI_num: aantal meldingen
        }
        f"{maand}_{jaar}": {
            ...
        }
    },
    storingen: {
        f"{maand}_{jaar}": {
            DI_num: aantal storingen,
            DI_num: aantal storingen
        }
        f"{maand}_{jaar}": {
            ...
        }
    }
}


Fucnties/Modules die geschreven moeten worden, zijn:
    -   [x] het opvragen van het gemiddelde aantal meldingen per maand, per jaar
    -   [x] het opvragen van het aantal meldingen in een gegeven maand, een gegeven jaar
    -   [x] module voor het filteren van meldingen of storingen op een te kiezen di nummer
    -   [ ] module voor het updaten en opslaan van de nieuw gegenereerde metadata
"""