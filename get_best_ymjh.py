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
    period = '1d'
    resualt_folder_path = 'E:/data/ymjh/'
    df_lst = []
    for symble in symble_lst:
        data = pd.read_csv(resualt_folder_path + 'state_ymjh_tb_' + '19' + '.csv')
        print(data)
        data = data[(data['ave_r'] > -1) & (data['max_retrace'] < 0.5) & (data['ann_ret'] > 0) &
                     (data['sharp'] > 0) & (data['trade_times'] > 0)]
        print(data)
        data['hold_days'] = data['trade_times'] * data['ave_hold_days']
        data['com_r'] = data['trade_times'] * data['ave_r']
        # if len(data_) > 0:
        #     if len(data_) < 100:
        #         df_lst.append(data_)
        #     else:
        #         df_lst.append(data_.sort_values(['sharp'], ascending=False).head(100))
    # tm_df = pd.concat(df_lst)
    lst = []
    for method, group in data.groupby(['art_N', 'art_n', 'period_s', 'period_l']):
        # if len(group)==3:
        #     lst.append(group)
        print(len(group))
        group_ = group[(group['e_time'] > '2019-08-29  00:00:00') & (group['s_time'] < '2017-02-01  9:30:00')]
        group_ = group
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
        row.append(group.com_r.sum() / group.trade_times.sum())
        row.append(group_.hold_days.sum()/group_.trade_times.sum())
        row.append(group.com_r.sum() / group_.hold_days.sum())
        lst.append(row)
        # if len(group) >= 1:
        #     lst.append(group.sort_values(['sharp'], ascending=False).head(5))

    df = pd.DataFrame(lst, columns=['method', 'num', 'sharp', 'ann_ret', 'trade_times', 'win_r', 'odds', 'max_retrace',
                                    'ave_r', 'ave_hold_days', 'ave_r_d'])
    print(df)
    df.to_csv(resualt_folder_path + 'best_ymjh_tb_' + period + '19.csv')
    # pd.concat(lst).to_csv('alpha_usdt_5' + str(tm) + '.csv')
