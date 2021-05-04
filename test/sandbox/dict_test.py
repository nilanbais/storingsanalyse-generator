import pandas as pd

asset_attribute_names = [
    {'asset1': {"sbs": "3453",
                   "asset beschrijving": "ja toch",
                   "locatie": "hier"},
        'asset2': {"sbs": "56756",
                   "asset beschrijving": "nah fam",
                   "locatie": "shi"}
        },
    {'asset1': {"sbs": "6563",
                   "asset beschrijving": "yas fam",
                   "locatie": "aye"},
        'asset2': {"sbs": "6363",
                   "asset beschrijving": "ja nee",
                   "locatie": "eh"}
        }]

r = pd.json_normalize(data=asset_attribute_names)
t = pd.DataFrame(asset_attribute_names[0])

# r = pd.json_normalize(data=asset_attribute_names[4])
# r = r.append(pd.json_normalize(data=asset_attribute_names[8]), ignore_index=True)
# li = []
# for k in asset_attribute_names.keys():
#     li.append(k)
#
# r.insert(loc=0, value=li, column='index')
