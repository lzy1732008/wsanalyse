import xlwt
import xlrd
import os
from xlutils.copy import copy


# rows:list
# colums:list
# data:list[list]
def createx(wsname, rows, colums, data ,dir):

    fnt = xlwt.Font()
    fnt.name = 'SimSun'
    fnt.bold = True
    fnt.height = 250
    wb = xlwt.Workbook()
    style = xlwt.easyxf('align: wrap on;')

    style.font = fnt

    ws = wb.add_sheet(wsname);


    #设置行
    for i in range(len(rows)):
        ws.write(i + 1, 0, rows[i] ,style)


    #设置列
    for i in range(len(colums)):
        ws.write(0, i + 1, colums[i] ,style)

    for i in range(len(colums)+1):
        ws.col(i).width = 256 * 40

    ws.panes_frozen = True
    ws.horz_split_pos = 1


    #录入数据
    for i in range(len(data)):
        for j in range(len(data[i])):
            ws.write(i+1,j+1,data[i][j])
    wb.save(dir+'/'+wsname+'_ft2jl.xls');



def getcolls(excelpath):
    excelfile = xlrd.open_workbook(excelpath)
    sheet = excelfile.sheet_by_index(0)
    rowls = []
    for i in range(1,sheet.ncols):
        # print(sheet.col_values(i))
        cell = sheet.cell_value(0,i)
        rowls.append(cell)
    return rowls


def getrowls(excelpath):
    excelfile = xlrd.open_workbook(excelpath)
    sheet = excelfile.sheet_by_index(0)
    colls = []
    for i in range(1,sheet.nrows):
        # print(sheet.col_values(i))
        cell = sheet.cell_value(i,0)
        colls.append(cell)
    return colls


def getexceldata(excelpath):
    data = []
    excelfile = xlrd.open_workbook(excelpath)
    sheet = excelfile.sheet_by_index(0)
    # print(sheet.name)
    for i in range(1,sheet.ncols):
        col = []
        # print(sheet.col_values(i))
        for j in range(1,sheet.nrows):
            cell = sheet.cell_value(j,i)
            # print(cell)
            # print(type(cell))
            if isinstance(cell,float) == True:
                col.append(cell)
            if isinstance(cell,str) == True:
                if cell.strip() == '':
                    col.append(0)
                else:
                    col.append(int(cell[0]))
            # print(col)
        data.append(col)
    return data


def alterexcel(excelapath,cols,rows,datas):
    p= xlrd.open_workbook(excelapath)
    wb = copy(p)
    sheet = wb.get_sheet(0)
    print(sheet.name)
    pdata = zip(cols,rows,datas)
    for col,row,data in pdata:
        sheet.write(int(row.strip())+1,int(col.strip())+1,data)
    wb.save(excelapath)

# getexceldata('../data/1w篇_事实到法条/000_273841.xml_ft2jl.xls')
# createx('ffff',['中华人民共和国刑法(2015)第一百三十三条:违反交通运输管理法规，因而发生重大事故，致人重伤、死亡或者使公私财产遭受重大损失的，处三年以下有期徒刑或者拘役；交通运输肇事后逃逸或者有其他特别恶劣情节的，处三年以上七年以下有期徒刑；因逃逸致人死亡的，处七年以上有期徒刑。'],['中华人民共和国刑法(2015)第一百三十三条:违反交通运输管理法规，因而发生重大事故，致人重伤、死亡或者使公私财产遭受重大损失的，处三年以下有期徒刑或者拘役；交通运输肇事后逃逸或者有其他特别恶劣情节的，处三年以上七年以下有期徒刑；因逃逸致人死亡的，处七年以上有期徒刑。'],[],'../data')