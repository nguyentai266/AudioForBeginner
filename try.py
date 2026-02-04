import numpy
import pandas

dataFrame=pandas.read_csv('C:/Users/nguye/Desktop/AudioForBeginner/sum.csv')


def parserDataByDutID(dataFrame,dutID,phase):
    for dut,g in dataFrame.groupby('dut_id'):
        print(dut)

        print(g)
        g.to_csv(f"test/{dut}.csv")
        


test=parserDataByDutID(dataFrame=dataFrame,dutID="",phase="spk-2_rb")
print(test)
