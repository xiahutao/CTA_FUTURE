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
    for (buy1, buy2) in k1_lst:
        for (sell1, sell2) in k2_lst:
            for percentile in percentile_lst:
                for (method_open, method_close) in method_lst:
                    df = pd.DataFrame([], columns=['date_time'])
                    for symble in index_code_lst:
                        try:
                            net = pd.read_csv(fold + 'net/adj%s_%s_%s_%s_%s_%s_%s_%s.csv' % (
                                symble, method_open, method_close, buy1, buy2, sell1, sell2, int(10 * percentile)))[
                                ['date_time', 'net']]
                            net.set_index(['date_time'])[['net']].plot(kind='line', grid=True)
                            plt.rcParams['font.sans-serif'] = ['SimHei']
                            title_str = '%s%s' % ('week_week_', symble)
                            plt.title(title_str)
                            # plt.savefig(fold + 'fig/' + title_str + '_position.png')
                            plt.show()
                            net['chg'] = net['net'] / net['net'].shift(1) - 1
                            df = df.merge(net[['date_time', 'chg']], on=['date_time'], how='outer')
                        except Exception as e:
                            print(str(e))
                    df = df.fillna(value=0).sort_values(['date_time'])
                    df = df.set_index(['date_time'])
                    df['net'] = df.sum(axis=1) / len(index_code_lst)
                    df['net'] = (1 + df['net']).cumprod()

                    # df.to_csv(fold + 'portfolio_net/future_net_%s_%s_%s_%s_%s_%s_%s_ls.csv' % (
                    # method_open, method_close, buy1, buy2, sell1, sell2, int(10 * percentile)))
                    # df[['net']].plot(kind='line', grid=True)
                    # plt.show()
                    net_lst_ = df.net.tolist()
                    ann_ROR = annROR(net_lst_, n)
                    total_ret = net_lst_[-1]
                    max_retrace = maxRetrace(net_lst_, n)
                    sharp = yearsharpRatio(net_lst_, n)
                    state_row = []

                    state_row.append(total_ret - 1)
                    state_row.append(ann_ROR)
                    state_row.append(sharp)
                    state_row.append(max_retrace)

                    state_row.append(percentile)
                    state_row.append(buy1)
                    state_row.append(buy2)
                    state_row.append(sell1)
                    state_row.append(sell2)
                    state_row.append(method_open + '_' + method_close)

                    state_lst.append(state_row)
    signal_state = pd.DataFrame(state_lst, columns=['total_ret', 'ann_ret', 'sharp',
                                                    'max_retrace', 'percentile', 'buy1', 'buy2', 'sell1',
                                                    'sell2', 'method'])
    print(signal_state)
    signal_state.to_csv(fold + 'sharp_kdj_macd_future' + '_adj.csv')
