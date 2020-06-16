# coding=utf-8
'''
Created on 7.9, 2018

@author: fang.zhang
'''
from __future__ import division
from backtest_func import *
import matplotlib.pyplot as plt
from matplotlib import style

style.use('ggplot')


if __name__ == '__main__':
    # os.getcwd()
    # print(os.path)
    n = 1
    # os.chdir(r'/Users/zhangfang/PycharmProjects')
    symble_lst = ['MA', 'JM', 'SN', 'AG', 'M', 'RB', 'RU', 'NI', 'AU',
                  'HC', 'AL', 'JD', 'TA', 'P']
    df = pd.DataFrame(columns=['date_time'])
    n_lst = [1]
    for symbol in symble_lst:
        csv = pd.read_csv('E:/data/ocm/net_' + symbol + '.csv')[['date_time', 'net']]\
            .assign(net=lambda df: df.net.pct_change(1))
        df = df.merge(csv, on=['date_time'], how='outer')

    df = df.sort_values(['date_time'])

    df = df.fillna(method='ffill').fillna(value=0).set_index(['date_time'], drop=True)
    print(df)
    # df = df[df['date_time'] >= '20170901']
    print(df)
    df['net_return'] = df.mean(axis=1)
    df['net_n'] = (1 + df.net_return).cumprod()
    print(df)
    df.reset_index(drop=False)[['date_time', 'net_n']].plot(
                                x='date_time', kind='line', grid=True)
    plt.xlabel('date_time')
    # plt.savefig('cl_trend/data/' + '组合净值' + str(n) + '.png')
    plt.show()
    # df.to_csv('cl_trend/data/net' + str(n) + '.csv')
    net_lst_new = df.net_n.tolist()
    ann_ROR = annROR(net_lst_new, n)
    max_retrace = maxRetrace(net_lst_new, n)
    sharp = yearsharpRatio(net_lst_new, n)

    # ann_ROR = annROR(net_lst_new, n)
    total_ret = net_lst_new[-1]
    # max_retrace_lst = [net_lst_new[i] for i in range(1, len(net_lst_new), int(1440 / n))]
    # max_retrace = maxRetrace(max_retrace_lst, n)
    # sharp = yearsharpRatio(max_retrace_lst, 1440)
    print('回测开始日期=', df.reset_index(drop=False).date_time.tolist()[0])
    print('回测结束日期=', df.reset_index(drop=False).date_time.tolist()[-1])
    print('总收益=', total_ret - 1)
    print('年化收益=', ann_ROR)
    print('夏普比率=', sharp)
    print('最大回撤=', max_retrace)