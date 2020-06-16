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

    percentile_lst = [1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    n = 1  # 回测周期
    period = '1d'
    method_lst = [('day', 'day'), ('week', 'day'), ('day', 'week'), ('week', 'week')]
    method_lst = [('week', 'day'), ('week', 'week')]
    k1_lst = [(20, 30), (20, 40), (15, 30), (15, 35), (20, 35), (15, 40)]  # kd下限
    k2_lst = [(70, 80), (60, 80), (70, 85), (65, 85), (65, 80), (60, 85)]  # kd上限
    signal_state_all_df = pd.read_csv(fold + 'state_kdj_macd_stock_ls' + '.csv')

    state_lst = []
    df = pd.DataFrame([], columns=['date_time'])
    columns = ['buy1', 'buy2', 'sell1', 'sell2', 'method', 'percentile']
    column = ['buy1', 'buy2', 'sell1', 'sell2', 'percentile']
    times = 'week_day'
    title = '多空:不同KD阈值对应平均夏普和年化收益'
    lst = []
    signal_state_all_df = signal_state_all_df[(signal_state_all_df['buy1'] == 15) & (signal_state_all_df['buy2'] == 40) &
                                              (signal_state_all_df['sell1'] == 70) & (signal_state_all_df['sell2'] == 85) &
                                              (signal_state_all_df['method'] == times)]
    # signal_state_all_df = signal_state_all_df[(signal_state_all_df['method'] == times)]
    for method, group in signal_state_all_df.groupby(column):
        row = []
        row.append(method)
        row.append(group.sharp.mean())
        row.append(group.ann_ret.mean())
        row.append(group.max_retrace.mean())
        lst.append(row)
    df = pd.DataFrame(lst, columns=['method', 'sharp', 'ann_ret', 'max_retrace'])
    df = df.set_index(['method'])


    df[['sharp', 'ann_ret']].plot(secondary_y='ann_ret')

    plt.rcParams['font.sans-serif'] = ['SimHei']
    title_str = '%s%s' % (times, title)
    plt.title(title_str)
    # plt.savefig(fold + 'fig/' + title_str + '_position.png')
    plt.show()


    print(df)
    df.to_csv(fold + 'sharp' + '4.csv')
