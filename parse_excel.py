import openpyxl
import json
def excel_to_json(name) -> str:
    with open('zam.json',encoding='utf-8') as f:
        zamen_dict = json.load(f)
    book = openpyxl.open(name,read_only=True)
    sheet = book.active
    date = sheet[2][0].value
    date = date.strftime('%d.%m.%y')
    zamen_dict[date] = []
    for row in sheet:
        if row[1].value != 'Класс':
            zamen_dict[date].append([row[1].value,row[2].value,row[3].value])
    print(zamen_dict)
    with open('zam.json', 'w',encoding='utf-8') as outfile:
        json.dump(zamen_dict, outfile,ensure_ascii=False)
    return date