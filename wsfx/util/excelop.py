import xlwt


# rows:list
# colums:list
# data:list[list]
def createx(wsname, rows, colums, data ,dir):
    wb = xlwt.Workbook()
    ws = wb.add_sheet(wsname);
    #设置行
    for i in range(len(rows)):
        ws.write(i + 1, 0, rows[i] )

    #设置列
    for i in range(len(colums)):
        ws.write(0, i + 1, colums[i] )

    #录入数据
    for i in range(len(data)):
        for j in range(len(data[i])):
            ws.write(i+1,j+1,data[i][j])
    wb.save(dir+'/'+wsname+'_ft2jl.xls');
