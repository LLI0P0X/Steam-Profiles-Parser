import steamReq
import asyncio
import xlsxwriter

def flt(st):
    return str.isspace(st) or str.isalpha(st) or str.isalnum(st)
def toExcel(lists, name):
    name = ''.join(filter(flt, name)).replace(' ', '_')
    with xlsxwriter.Workbook(f'{name}.xlsx', options={'strings_to_urls': False}) as workbook:
        worksheet = workbook.add_worksheet()

        for row in range(len(lists)):
            for col in range(len(lists[row])):
                if len(lists[row][col]) == 0:
                    continue
                if lists[row][col][0] == '=':
                    lists[row][col] = "'" + lists[row][col]
            worksheet.write_row(row, 0, lists[row])


async def main():
    name = input('Введите ник\n')
    data = await steamReq.getDataByNick(name)

    for q in data:
        print(q)

    toExcel(data, name)


if __name__ == '__main__':
    asyncio.run(main())
