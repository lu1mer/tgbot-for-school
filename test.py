# # import openpyxl
# import json
import datetime
# # def exceimel(name):
# #     book = openpyxl.open(name,read_only=True)
# #     sheet = book.active
# #     date = sheet[2][0].value
# #     date = date.strftime('%m.%d.%y')
# #     zamen_dict = {date:[]}
# #     for row in sheet:
# #         if row[1].value != 'Класс':
# #             zamen_dict[date].append([row[1].value,row[2].value,row[3].value])
# #     print(zamen_dict)
# #     with open('zam.json', 'w',encoding='utf-8') as outfile:
# #         json.dump(zamen_dict, outfile,ensure_ascii=False)
# # excel('zam.xlsx')
# with open('zam.json',encoding='utf-8') as f:
#     templates = json.load(f)
# print(templates)
d = 30
print((datetime.date.today() + datetime.timedelta(days=d)).strftime('%d.%m.%y'))