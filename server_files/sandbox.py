"""
test_template has next vars:
name
function
adres
tel
e-mail
tekst
row_contents
"""
import os
import docxtpl
import docx
from docxcompose.composer import Composer

tekst = """
multi line string vol met bullshiii puur om te testen met 
een 
multi 
line 
string.
"""

data_package = {"name": "young baisie",
                "function": "Big Man",
                "adres": "On the Block",
                "tel": "0223 ja toch",
                "mail": "bisoe@skrt.io",
                "tekst": tekst,
                "row_contents": [
                    {"description": "a b c",
                     "value": "ja",
                     "bool": True},
                    {"description": "a b c",
                     "value": "nee",
                     "bool": True},
                    {"description": "a b c",
                     "value": "prrt",
                     "bool": True}
                ]
                }

print(os.getcwd())

doc = docxtpl.DocxTemplate("test_template_2.docx")
doc.render(data_package)
doc.save("test_render.docx")
