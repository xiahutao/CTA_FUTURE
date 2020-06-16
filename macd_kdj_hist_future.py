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

def plot(df, xlabel, ylabel, title, path):
    plt.hist(df, bins='auto', rwidth=0.85)
    plt.grid(axis='y')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title + ' mean=%s' % str(np.around(df.mean(), 4)))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    plt.savefig(path + title + '.png')
    plt.show()


if __name__ == '__main__':
    fold = 'e:/kdj_macd/'
    fold_data = 'e:/kdj_macd/data/'

    start_day = '2005-01-01'
    end_day = datetime.date.today().strftime('%Y-%m-%d')

    index_code_lst = ['C', 'CS', 'A', 'B', 'M', 'RM', 'Y', 'P', 'OI', 'L', 'V', 'PP', 'TA', 'RU', 'BU', 'MA', 'SC', 'FU',
                   'AL', 'ZN', 'CU', 'PB', 'NI', 'SN', 'J', 'JM', 'I', 'RB', 'HC', 'ZC', 'SF', 'SM', 'FG', 'IF',
                   'IH', 'IC', 'T', 'TF', 'AG', 'AU', 'JD', 'AP', 'CJ', 'CF', 'SR']
    percentile_lst = [1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

    n = 1  # 回测周期
    period = '1d'
    method_lst = [('week', 'day'), ('week', 'week'), ('day', 'day'), ('day', 'week')]
    # method_lst = [('week', 'day')]
    k1_lst = [(20, 30), (20, 40), (15, 30), (15, 35), (20, 35), (15, 40)]  # kd下限
    k2_lst = [(70, 80), (60, 80), (70, 85), (65, 85), (65, 80), (60, 85)]  # kd上限
    k1_lst = [(20, 30)]  # kd下限
    k2_lst = [(70, 80)]  # kd上限
    percentile_lst = [1]

    state_lst = []
    df = pd.DataFrame([], columns=['date_time'])
    signal_df = pd.read_csv(fold + 'ret_hold3days_0adj.csv')
    group = signal_df
    # group['ret_aveday'] = group['ret'] / group['hold_day']
    for method, group in signal_df.groupby(['method']):
        # plot(group.ret, 'return', 'Frequency', 'all' + '_' + method + '_收益分布', fold + 'fig/')
        # plot(group.ret_aveday, 'return_everyday', 'Frequency', 'all' + '_' + method + '_日均收益分布', fold + 'fig/')
        plot(group.ret_3days, 'return_holddays3', 'Frequency', 'all' + '_' + method + '_持仓3日收益分布',
             fold + 'fig/fig/')
    lst = []
    for method, group in signal_df.groupby(['symble', 'method']):

        # group['ret_aveday'] = group['ret'] / group['hold_day']
        # plot(group.ret, 'return', 'Frequency', method[0][:-9] + '_' + method[1] + '_收益分布', fold + 'fig/')
        # plot(group.ret_aveday, 'return_everyday', 'Frequency', method[0][:-9] + '_' + method[1] + '_日均收益分布', fold + 'fig/')
        plot(group.ret_3days, 'return_holddays3', 'Frequency', method[0][:-9] + '_' + method[1] + '_持仓3日收益分布',
             fold + 'fig/fig/')
        # lst.append([group.ret.mean, len(group)])



