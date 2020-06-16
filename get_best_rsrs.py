# coding=utf-8
'''
Created on 7.9, 2018
@author: fang.zhang
'''
from __future__ import division
from backtest_func import *

if __name__ == '__main__':
    symble_lst = ['M']
    time_lst = ['240']

    df_lst = []
    for symble in symble_lst:
        data = pd.read_csv('E:/data/tcs/' + 'state_rsrs_' + '44' + '.csv')
        print(data)
        data = data[(data['ave_r'] > -1) & (data['max_retrace'] < 0.5) & (data['ann_ret'] > 0) &
                     (data['sharp'] > 0) & (data['trade_times'] > 0)]
        print(data)
        data['hold_days'] = data['trade_times'] * data['ave_hold_days']
        # if len(data_) > 0:
        #     if len(data_) < 100:
        #         df_lst.append(data_)
        #     else:
        #         df_lst.append(data_.sort_values(['sharp'], ascending=False).head(100))
    # tm_df = pd.concat(df_lst)
    lst = []
    for method, group in data.groupby(['art_N', 'art_n', 'ma', 'k']):
        # if len(group)==3:
        #     lst.append(group)
        print(len(group))
        group_ = group[(group['e_time'] == '2019-08-30') & (group['s_time'] < '2017-03-01')]
        print(len(group_))
        row = []
        row.append(method)
        row.append(len(group))
        row.append(group.sharp.mean())
        row.append(group.ann_ret.mean())
        row.append(group_.trade_times.mean())
        row.append(group.win_r.mean())
        row.append(group.odds.mean())
        row.append(group_.max_retrace.mean())
        row.append(group.ave_r.mean())
        row.append(group_.hold_days.sum()/group_.trade_times.sum())
        lst.append(row)
        # if len(group) >= 1:
        #     lst.append(group.sort_values(['sharp'], ascending=False).head(5))

    df = pd.DataFrame(lst, columns=['method', 'num', 'sharp', 'ann_ret', 'trade_times', 'win_r', 'odds', 'max_retrace',
                                    'ave_r', 'ave_hold_days'])
    print(df)
    df.to_csv('E:/data/tcs/' + 'best_state_tcs_' + '442' + '.csv')
    # pd.concat(lst).to_csv('alpha_usdt_5' + str(tm) + '.csv')
