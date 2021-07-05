"""
This file contains a dictionary of the names as given to the columns and the corresponding attribute name as used
in the Maximo Database. In theory this as to make it easier to change to code generating the report straight from
the source without the use of a staging_file in which the maintenance engineers have to manually set the value of
a column.
Attribute names are NOT given in a table.column lay-out (only the column name is given)
"""

# MAN (Mapped Attribute Names)
"""
Alle velden waar geen comment bij staan om een tabel te specificeren, behoren tot de Workorder tabel
"""
workorder_attribute_names = {"werkorder": "wonum",
                             "status": "status",
                             "rapport datum": "reportdate",
                             "werkorder beschrijving": "description",
                             "asset nummer": "assetnum",
                             "asset nummer 2": "assetnum2",
                             "probleem code": "problemcode",
                             "beschrijving probleem": "gmbctschcodering8",
                             "oorzaak code": "fr1code",
                             "beschrijving oorzaak": "gmbctschcodering9",
                             "oplos code": "fr2code",
                             "oplossing beschrijving": "gmb_solution",
                             "uitgevoerde werkzaamheden": "gmbctschcodering17",
                             "tijdstip monteur ter plaatse": "gmbctschcodering24",
                             "streefdatum start": "targstartdate",
                             "geplande start": "schedstart",
                             "werkelijke start": "actstart",
                             "tijdstip einde werkzaamheden": "actfinish",
                             "tijdstip afmelding": "gmbctschcodering35",
                             "tijdstip validatie": "gmbctschcodering33",
                             "funcitoneel herstel": "gmbctschcodering36",
                             "definitief herstel": "gmbctschcodering37",
                             "is financieel nadeel": "gmbisfinnadeel",
                             "gmblocation3": "gmblocation3",
                             "gemeld asset": "gmb_gemeldasset",
                             "vestiging": "siteid"
                             }

asset_attribute_names = {"sbs": "gmblocation",
                         "asset beschrijving": "description",
                         "locatie": "location",
                         # "sbs2": "gmblocation2",
                         # "asset beschrijving 2": "description",
                         # "locatie 2": "location2"
                         }

"""
van onderstaande is de eerste gesorteerd per 1 of 2 
de tweede is gesorteerd per data (assetnum 1&2, sbs 1&2 enz.)
"""
staging_file_columns1 = ['werkorder', 'status', 'rapport datum', 'werkorder beschrijving',
                         'asset nummer', 'asset beschrijving', 'sbs', 'sbs omschrijving', 'locatie', 'locatie omschrijving',
                         'asset nummer 2', 'asset beschrijving 2', 'sbs 2', 'sbs 2 omschrijving', 'locatie 2', 'locatie 2 omschrijving',
                         'probleem code', 'beschrijving probleem', 'oorzaak code', 'beschrijving oorzaak', 'oplos code', 'oplossing beschrijving', 'uitgevoerde werkzaamheden',
                         'tijdstip monteur ter plaatse', 'streefdatum start', 'geplande start', 'werkelijke start',
                         'tijdstip einde werkzaamheden', 'tijdstip afmelding', 'tijdstip validatie',
                         'funcitoneel herstel', 'definitief herstel', 'is financieel nadeel', 'gmblocation3',
                         'gemeld asset', 'vestiging']

staging_file_columns2 = ['werkorder', 'status', 'rapport datum', 'werkorder beschrijving',
                         'asset nummer', 'asset beschrijving', 'asset nummer 2', 'asset beschrijving 2',
                         'sbs', 'sbs omschrijving', 'sbs 2', 'sbs 2 omschrijving',
                         'locatie', 'locatie omschrijving', 'locatie 2', 'locatie 2 omschrijving',
                         'probleem code', 'beschrijving probleem', 'oorzaak code', 'beschrijving oorzaak', 'oplos code',
                         'oplossing beschrijving', 'uitgevoerde werkzaamheden', 'tijdstip monteur ter plaatse',
                         'streefdatum start', 'geplande start', 'werkelijke start', 'tijdstip einde werkzaamheden',
                         'tijdstip afmelding', 'tijdstip validatie', 'funcitoneel herstel', 'definitief herstel',
                         'is financieel nadeel', 'gmblocation3', 'gemeld asset', 'vestiging']

# dt_attributes contains every attribute that contains a datetime object AND ISN'T reportdate
dt_attributes = ['gmbctschcodering24', 'targstartdate', 'schedstart', 'actstart', 'actfinish',
                 'gmbctschcodering35', 'gmbctschcodering33', 'gmbctschcodering36', 'gmbctschcodering37']
