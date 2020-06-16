from __future__ import division
from backtest_func import *
import matplotlib.pyplot as plt
from matplotlib import style
import pymongo
from arctic import Arctic, TICK_STORE, CHUNK_STORE
from jqdatasdk import *
import copy
import talib as tb

# auth('18610039264', 'zg19491001')
style.use('ggplot')

auth('15658001226', 'taiyi123')
myclient = pymongo.MongoClient('mongodb://juzheng:jz2018*@192.168.2.201:27017/')
jzmongo = Arctic(myclient)


if __name__ == '__main__':
    fold = 'e:/kdj_macd/'
    fold_data = 'e:/kdj_macd/data/'

    start_day = '2005-01-01'
    end_day = datetime.date.today().strftime('%Y-%m-%d')

    index_code_lst = ['000002.XSHE', '600048.XSHG', '600018.XSHG', '600054.XSHG', '600138.XSHG', '600977.XSHG',
                      '601111.XSHG', '002739.XSHE']
    signal_state_all_df = pd.read_csv(fold + 'signal_kdj_macd_' + str(len(index_code_lst)) + '.csv')
    signal_state = pd.read_csv(fold + 'state_kdj_macd_' + str(len(index_code_lst)) + '.csv')
    # state_all_df = []
    # signal_all_df = []
    # for x in range(6):
    #     state_all_df.append(pd.read_csv(fold + 'state_kdj_macd_future_' + str(x) + '.csv'))
    #     signal_all_df.append(pd.read_csv(fold + 'signal_kdj_macd_future_' + str(x) + '.csv'))
    # state_all_df = pd.concat(state_all_df)
    # signal_all_df = pd.concat(signal_all_df)
    state_all_df = pd.read_csv(fold + 'state_kdj_macd_future_10' + '.csv')
    signal_all_df = pd.read_csv(fold + 'signal_kdj_macd_future_' + str(10) + '.csv')

    lst = []
    for method, group in signal_all_df.groupby(['buy1', 'buy2', 'sell1', 'sell2', 'method', 'percentile']):
        row = []
        win_r, odds, ave_r, mid_r = get_winR_odds(group.ret.tolist())
        row.extend(method)
        row.append(win_r)
        row.append(odds)
        row.append(ave_r)
        row.append(len(group))
        row.append(group.hold_day.mean())
        lst.append(row)
    ret = pd.DataFrame(lst, columns=['buy1', 'buy2', 'sell1', 'sell2', 'method', 'percentile', 'winr', 'odds', 'ave_r',
                                     'trading_times', 'ave_hold_day'])
    ret.to_csv(fold + 'kdj_macd_' + '10' + '.csv')
    # sharp = pd.read_csv(fold + 'sharp_kdj_macd_future' + '_adj.csv')
    # sharp = sharp.merge(ret, on=['buy1', 'buy2', 'sell1', 'sell2', 'method', 'percentile'])
    # print(sharp)
    # sharp.to_csv(fold + 'state_kdj_macd_future_sharp_winr_adj.csv')

