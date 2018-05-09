from wsfx.NN.ss2ft.predict import CnnModel as ssCnn
from wsfx.NN.ft2jl.predict import CnnModel as jlCnn
from wsfx.util.wsfun import getJLMatchObject,getSSMatchObject,getFTList
from wsfx.util.contentop import cutcontent


def predictssws(wspath):
    sf_model = ssCnn()
    ssStrls = cutcontent(getSSMatchObject(wspath))
    ftmcls, ftnrls = getFTList(wspath)
    outputss = []
    #事实到法条
    for ss in ssStrls:
        print(ss)
        for ft in ftnrls:
            print(ft)
            print(sf_model.predict(ss,ft))



def predictjlws(wspath):
    fj_model = jlCnn()
    jlStrls = cutcontent(getJLMatchObject(wspath))
    ftmcls, ftnrls = getFTList(wspath)
    # 法条到结论
    for jl in jlStrls:
        print(jl)
        for ft in ftnrls:
            print(ft)
            print(fj_model.predict(jl, ft))


predictjlws('2574.xml')



