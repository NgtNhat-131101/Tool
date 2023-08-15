import xlsxwriter


def create_excel_file(data, file_name='test.xlsx'):
    workbook = xlsxwriter.Workbook(file_name)
    worksheet = workbook.add_worksheet('Sheet1')

    format = workbook.add_format({
        'text_wrap': 1,
        'border': 1,
        'align': 'center',
        'valign': 'center',
    })

    format1 = workbook.add_format({
        'text_wrap': 1,
        'border': 1,
        'align': 'left',
        'valign': 'left',
    })

    cell_format = workbook.add_format({
        'border': 1,
        'align': 'center',
        'valign': 'center',
    })

    worksheet.merge_range('A1:AL1', 'Lô hàng ngày dd.mm.yyyy', format1)
    worksheet.merge_range('AM1:AM6', 'Ghi chú', format)
    worksheet.merge_range('A2:A6', 'STT', format)
    worksheet.merge_range('B2:B6', 'MAC', format)
    worksheet.merge_range('C2:C6', 'Công suất thu', format)
    worksheet.merge_range('AL2:AL6', 'Kết luận', format)
    worksheet.merge_range('D2:M2', 'Lần 1', format)
    worksheet.merge_range('N2:W2', 'Lần 2', format)
    worksheet.merge_range('X2:AG2', 'Lần 3', format)
    worksheet.merge_range('AH2:AJ3', 'IPTV', format)
    worksheet.merge_range('AK2:AK3', 'VoD', format)

    worksheet.merge_range('D3:G3', 'Dây', format)
    worksheet.merge_range('N3:Q3', 'Dây', format)
    worksheet.merge_range('Y3:AA3', 'Dây', format)
    worksheet.merge_range('H3:M3', 'Wifi', format)
    worksheet.merge_range('R3:W3', 'Wifi', format)
    worksheet.merge_range('AB3:AG3', 'Wifi', format)

    worksheet.merge_range('D4:D6', 'Ping time (Khi ko down)', format)
    worksheet.merge_range('E4:E6', 'Down rate', format)
    worksheet.merge_range('F4:F6', 'Ổn định khi down', format)
    worksheet.merge_range('G4:G6', 'Kết luận', format)
    worksheet.merge_range('H4:H6', 'Ping time (Khi ko down)', format)
    worksheet.merge_range('I4:J4', 'Down rate', format)
    worksheet.write(4, 8, 'RSSI - 40dBm', format)
    worksheet.write(4, 9, 'RSSI - 55dBm', format)
    worksheet.write(5, 8, '2.4G', format)
    worksheet.write(5, 9, '5G', format)
    worksheet.merge_range('K4:K6', 'Ổn định khi down', format)
    worksheet.merge_range('L4:L6', 'Khả năng tự kết nối lại', format)
    worksheet.merge_range('M4:M6', 'Kết luận', format)

    worksheet.merge_range('N4:N6', 'Ping time (Khi ko down)', format)
    worksheet.merge_range('O4:O6', 'Down rate', format)
    worksheet.merge_range('P4:P6', 'Ổn định khi down', format)
    worksheet.merge_range('Q4:Q6', 'Kết luận', format)
    worksheet.merge_range('R4:R6', 'Ping time (Khi ko down)', format)
    worksheet.merge_range('S4:T4', 'Down rate', format)
    worksheet.write(4, 18, 'RSSI - 40dBm', format)
    worksheet.write(4, 19, 'RSSI - 55dBm', format)
    worksheet.write(5, 18, '2.4G', format)
    worksheet.write(5, 19, '5G', format)
    worksheet.merge_range('U4:U6', 'Ổn định khi down', format)
    worksheet.merge_range('V4:V6', 'Khả năng tự kết nối lại', format)
    worksheet.merge_range('W4:W6', 'Kết luận', format)

    worksheet.merge_range('X4:X6', 'Ping time (Khi ko down)', format)
    worksheet.merge_range('Y4:Y6', 'Down rate', format)
    worksheet.merge_range('Z4:Z6', 'Ổn định khi down', format)
    worksheet.merge_range('AA4:AA6', 'Kết luận', format)
    worksheet.merge_range('AB4:AB6', 'Ping time (Khi ko down)', format)
    worksheet.merge_range('AC4:AD4', 'Down rate', format)
    worksheet.write(4, 28, 'RSSI - 40dBm', format)
    worksheet.write(4, 29, 'RSSI - 55dBm', format)
    worksheet.write(5, 28, '2.4G', format)
    worksheet.write(5, 29, '5G', format)
    worksheet.merge_range('AE4:AE6', 'Ổn định khi down', format)
    worksheet.merge_range('AF4:AF6', 'Khả năng tự kết nối lại', format)
    worksheet.merge_range('AG4:AG6', 'Kết luận', format)

    worksheet.merge_range('AH4:AH6', 'Độ ổn định', format)
    worksheet.merge_range('AI4:AI6', 'Thay đổi kênh liên tục', format)
    worksheet.merge_range('AJ4:AJ6', 'Xem nhiều kênh một lúc', format)
    worksheet.merge_range('AK4:AK6', 'Độ ổn định', format)

    row = 6
    for item in data:
        worksheet.write_row(row, 0, item, cell_format=cell_format)
        row += 1

    workbook.close()
    return workbook


if __name__ == '__main__':
    data = list()
    for i in range(10):
        data.append(
            'a s d f g h j k l z x c v b n m q w e r t y u i o'.split(' '))
    create_excel_file(data)
    print('Finish')
