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
                             "sbs": "gmblocation",
                             "sbs2": "gmblocation2",
                             "probleemcode": "problemcode",
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
                             "Gmblocation3": "gmblocation3",
                             "Gemeld asset": "gmb_gemeldasset"
                             }

asset_attribute_names = {"activum": "assetnum",
                         "asset beschrijving": "description",
                         "sbs omschrijving": "gmbdescription",
                         "vestiging": "siteid"
                         }

locations_attibute_names = {"locatie": "location",
                            "locatie omschrijving": "description"
                            }

all_attribute_names = dict(workorder_attribute_names, **asset_attribute_names, **locations_attibute_names)
