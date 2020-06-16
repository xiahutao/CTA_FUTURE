# coding=utf-8
'''
Created on 9.30, 2018
适用于btc/usdt，btc计价并结算
@author: fang.zhang
'''
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


# 获取价格
def stock_price(sec, sday, eday):
    """
    输入 股票代码，开始日期，截至日期
    输出 个股的后复权的开高低收价格
    """
    q = query(finance.GLOBAL_IDX_DAILY).filter(finance.GLOBAL_IDX_DAILY.code == sec).order_by(
        finance.GLOBAL_IDX_DAILY.day.desc())
    temp = finance.run_query(q)[
        ['day', 'name', 'code', 'open', 'high', 'low', 'close', 'volume']] \
        .assign(day=lambda df: df.day.apply(lambda x: str(x)[:10])) \
        .rename(columns={'day': 'trade_date', 'code': 'stock_cpde'})
    temp = temp[(temp['trade_date'] >= sday) & (temp['trade_date'] <= eday)].sort_values(['trade_date'])
    return temp


def get_stock_code_list():
    db_index = jzmongo['stock_raw.stock_index']
    stock_df = db_index.read('all')
    code_list = list(stock_df.iloc[-1].dropna().index)
    return code_list


def trans_heng_float(x):
    if x == '--':
        x = None
    return x


def stock_price_jz(sec, sday, eday):
    """
    输入 股票代码，开始日期，截至日期
    输出 个股的后复权的开高低收价格
    """
    temp = jzmongo['stock_raw.stock_1d_jq_post'].read(sec)
    temp = temp[temp['volume'] > 0]
    temp['date_time'] = temp.index
    temp = temp.assign(date_time=lambda df: df.date_time.apply(lambda x: str(x)[:10]))

    temp = temp.assign(high=lambda df: df.high.apply(lambda x: trans_heng_float(x))) \
        .assign(open=lambda df: df.open.apply(lambda x: trans_heng_float(x))) \
        .assign(low=lambda df: df.high.apply(lambda x: trans_heng_float(x)))[
        ['high', 'open', 'low', 'close', 'date_time']].dropna()
    temp = temp[(temp['date_time'] >= sday) & (temp['date_time'] <= eday)].sort_values(['date_time'])

    temp[['high', 'open', 'low', 'close']] = temp[['high', 'open', 'low', 'close']].astype(float)
    return temp


def get_normal_future_index_code():
    temp = get_all_securities(types=['futures'])
    temp['index_code'] = temp.index
    temp['idx'] = temp['index_code'].apply(lambda x: x[-9:-5])
    temp = temp[temp['idx'] == '8888']
    temp['symbol'] = temp['index_code'].apply(lambda x: x[:-9])
    temp = temp[['index_code', 'symbol']].set_index(['symbol'])
    code_dic = {}
    for idx, _row in temp.iterrows():
        code_dic[idx] = _row.index_code
    return code_dic


def get_normal_future_contract_code():
    temp = get_all_securities(types=['futures'])
    temp['index_code'] = temp.index
    temp['symbol'] = temp['index_code'].apply(lambda x: x[:-5])
    temp = temp[['index_code', 'symbol']].set_index(['symbol'])

    return temp


def stock_price_cgo(sec, sday, eday):
    """
    输入 股票代码，开始日期，截至日期
    输出 个股的后复权的开高低收价格
    """
    temp = get_price(sec, start_date=sday, end_date=eday, frequency='daily', fields=None, skip_paused=True, fq='pre',
                     count=None).reset_index() \
        .rename(columns={'index': 'date_time'}) \
        .assign(date_time=lambda df: df.date_time.apply(lambda x: str(x)[:10]))
    temp['stock_code'] = sec
    return temp


def KDJ(data, N=9, M1=3, M2=3):
    datelen = len(data)
    data = data[['date_time', 'open', 'high', 'low', 'close']]
    array = np.array(data)
    kdjarr = []
    k_lst = []
    d_lst = []
    j_lst = []

    for i in range(datelen):
        if i - N < 0:
            b = 0
        else:
            b = i - N + 1
        rsvarr = array[b:i + 1, 0:5]
        rsv = (float(rsvarr[-1, -1]) - float(min(rsvarr[:, 3]))) / (
                float(max(rsvarr[:, 2])) - float(min(rsvarr[:, 3]))) * 100
        if i == 0:
            k = rsv
            d = rsv
        else:
            k = 1 / float(M1) * rsv + (float(M1) - 1) / M1 * float(kdjarr[-1][2])
            d = 1 / float(M2) * k + (float(M2) - 1) / M2 * float(kdjarr[-1][3])
        j = 3 * k - 2 * d
        k_lst.append(k)
        d_lst.append(d)
        j_lst.append(j)
        kdjarr.append(list((rsvarr[-1, 0], rsv, k, d, j)))

    return k_lst, d_lst, j_lst


if __name__ == '__main__':
    os.getcwd()
    print(os.path)
    t0 = time.time()
    fold = 'e:/kdj_macd/'
    fold_data = 'e:/kdj_macd/data/'

    start_day = '2009-01-01'
    end_day = datetime.date.today().strftime('%Y-%m-%d')
    index_code_lst = get_stock_code_list()
    index_code_lst = ['C', 'CS', 'A', 'B', 'M', 'RM', 'Y', 'P', 'OI', 'L', 'V', 'PP', 'TA', 'RU', 'BU', 'MA', 'SC', 'FU',
                   'AL', 'ZN', 'CU', 'PB', 'NI', 'SN', 'J', 'JM', 'I', 'RB', 'HC', 'ZC', 'SF', 'SM', 'FG', 'IF',
                   'IH', 'IC', 'T', 'TF', 'AG', 'AU', 'JD', 'AP', 'CJ', 'CF', 'SR']
    # index_code_lst = ['C', 'CS', 'A', 'B', 'M', 'RM', 'Y']
    normalize_code_future = get_normal_future_index_code()
    percentile_lst = [1, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    x = 0

    n = 1  # 回测周期
    period = '1d'
    method_lst = [('day', 'day'), ('week', 'day'), ('day', 'week'), ('week', 'week')]
    method_lst = [('week', 'day'), ('week', 'week')]
    k1_lst = [(20, 30), (20, 40), (15, 30), (15, 35), (20, 35), (15, 40)]  # kd下限
    k2_lst = [(70, 80), (60, 80), (70, 85), (65, 85), (65, 80), (60, 85)]  # kd上限
    # percentile_lst = [1]
    # k1_lst = [(20, 30)]  # kd下限
    # k2_lst = [(70, 80)]  # kd上限

    lever_lst = [1]  # 杠杆率，btc初始仓位pos=1,usdt初始仓位pos=0;做多情况下，btc仓位1+lever,usdt仓位-lever;
    # 做空情况下，btc仓位1-lever,usdt仓位lever

    fee = 0.00011
    date_lst = [('2008-01-01', '2009-12-31'), ('2010-01-01', '2011-12-31'), ('2012-01-01', '2013-12-31'),
                ('2014-01-01', '2015-12-31'),
                ('2016-01-01', '2017-12-31'), ('2018-01-01', '2019-12-31')]
    date_lst = [('2010-01-01', '2020-12-31')]
    df_lst = []
    lst = []
    state_lst = []
    signal_state_all_lst = []
    for index_code in index_code_lst:
        try:
            symble = normalize_code_future[index_code]
            data_daily = stock_price_cgo(symble, start_day, end_day)[
                ['date_time', 'open', 'high', 'low', 'close']]
            data_daily['time'] = pd.to_datetime(data_daily['date_time'])
            data_daily.index = data_daily['time']
            data_daily = data_daily.drop(['time'], axis=1)
            data_week = data_daily.resample('W').last()
            data_week['date_time'] = data_daily['date_time'].resample('W').last()
            data_week['open'] = data_daily['open'].resample('W').first()
            data_week['high'] = data_daily['high'].resample('W').max()
            data_week['low'] = data_daily['low'].resample('W').min()
            data_week['close'] = data_daily['close'].resample('W').last()
            data_week = data_week.dropna()

            data_week['k_week'], data_week['d_week'], data_week['j_week'] = KDJ(data_week, 9, 3, 3)
            data_week['MACD'], data_week['MACDsignal'], data_week['macd_week'] = talib.MACDEXT(
                data_week['close'].values, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1, signalperiod=9,
                signalmatype=1)
            data_week = data_week.drop(['MACD', 'MACDsignal'], axis=1)

            data_daily['k_day'], data_daily['d_day'], data_daily['j_day'] = KDJ(data_daily, 9, 3, 3)
            data_daily['MACD'], data_daily['MACDsignal'], data_daily['macd_day'] = talib.MACDEXT(
                data_daily['close'].values, fastperiod=12, fastmatype=1, slowperiod=26, slowmatype=1, signalperiod=9,
                signalmatype=1)
            data_daily = data_daily.drop(['MACD', 'MACDsignal'], axis=1) \
                .merge(data_week[['k_week', 'd_week', 'macd_week', 'date_time']], on=['date_time'],
                       how='left').sort_values(
                ['date_time'])
            data_daily = data_daily.fillna(method='ffill')

            for (method_open, method_close) in method_lst:

                data = data_daily
                data['close_1'] = data.close.shift(1)
                data['k_d_open'] = data['k_' + method_open].shift(1) - data['d_' + method_open].shift(1)
                data['k_d_open_1'] = data['k_d_open'].shift(1)
                data['d_open'] = data['d_' + method_open].shift(1)
                data['k_open'] = data['k_' + method_open].shift(1)
                data['macd_open'] = data['macd_' + method_open].shift(1)
                data['macd_open_abs'] = np.abs(data['macd_open'])
                data['k_d_close'] = data['k_' + method_close].shift(1) - data['d_' + method_close].shift(1)
                data['k_d_close_1'] = data['k_d_close'].shift(1)
                data['d_close'] = data['d_' + method_close].shift(1)
                data['k_close'] = data['k_' + method_close].shift(1)
                data['macd_close'] = data['macd_' + method_close].shift(1)
                data['macd_close_abs'] = np.abs(data['macd_close'])
                data = data.dropna()

                data['rank_open'] = data.macd_open_abs.rank(method='min').astype(int)
                data['percentile_open'] = data['rank_open'] / len(data)

                data['rank_close'] = data.macd_close_abs.rank(method='min').astype(int)
                data['percentile_close'] = data['rank_close'] / len(data)
                # data.to_csv(fold_data + symble + '1.csv')

                for (buy1, buy2) in k1_lst:
                    for (sell1, sell2) in k2_lst:
                        for percentile in percentile_lst:
                            group_ = data.dropna()
                            print(symble)
                            status = -10000
                            signal_lst = []
                            trad_times = 0
                            net = 1
                            net_lst = []
                            pos_lst = []
                            pos = 0
                            low_price_pre = 0
                            high_price_pre = 100000000
                            long_stop = False
                            short_stop = False
                            for idx, _row in group_.iterrows():
                                condition_bk = (_row.k_open < buy2) and (_row.d_open > buy1) and (_row.k_d_open > 0) and \
                                              (_row.k_d_open_1 < 0) and (_row.percentile_open <= percentile)
                                condition_sp = (_row.k_close > sell1) and (_row.d_close < sell2) and (
                                            _row.k_d_close < 0) and (_row.k_d_close_1 > 0)
                                condition_sp = (_row.k_d_close < 0) and (_row.k_d_close_1 > 0)
                                condition_sk = (_row.k_open > sell1) and (_row.d_open < sell2) and (_row.k_d_open < 0) and \
                                               (_row.k_d_open_1 > 0) and (_row.percentile_open <= percentile)
                                condition_bp = (
                                        _row.k_d_close > 0) and (_row.k_d_close_1 < 0)
                                if pos == 0:
                                    if condition_bk:
                                        cost = _row.open * (1 + fee)
                                        pos = 1
                                        s_time = _row.date_time
                                        hold_price = []
                                        high_price = []
                                        hold_price.append(cost / (1 + fee))
                                        high_price.append(cost / (1 + fee))
                                        high_price.append(_row.high)
                                        net = (pos * _row.close / cost + (1 - pos)) * net
                                    elif condition_sk:
                                        cost = _row.open * (1 - fee)
                                        pos = -1
                                        s_time = _row.date_time
                                        hold_price = []
                                        low_price = []
                                        hold_price.append(cost / (1 - fee))
                                        low_price.append(cost / (1 - fee))
                                        low_price.append(_row.low)
                                        net = ((1 + pos) - pos * (2 - _row.close / cost)) * net
                                    else:
                                        net = net
                                elif pos > 0:
                                    if condition_sk:
                                        s_price = _row.open * (1 - fee)
                                        trad_times += 1
                                        net1 = pos * s_price / _row.close_1 + (1 - pos)
                                        ret = s_price / cost - 1
                                        e_time = _row.date_time
                                        signal_row = []
                                        signal_row.append(symble)
                                        signal_row.append(percentile)
                                        signal_row.append(buy1)
                                        signal_row.append(buy2)
                                        signal_row.append(sell1)
                                        signal_row.append(sell2)
                                        signal_row.append(method_open + '_' + method_close)
                                        signal_row.append(s_time)
                                        signal_row.append(e_time)
                                        signal_row.append(cost)
                                        signal_row.append(s_price)
                                        signal_row.append(ret)
                                        signal_row.append((max(high_price) / cost) - 1)
                                        signal_row.append(len(hold_price))
                                        signal_row.append(pos)
                                        signal_row.append('spk')
                                        signal_lst.append(signal_row)
                                        pos = -1
                                        net2 = (1 + pos) - pos * (2 - _row.close / cost)
                                        hold_price = []
                                        low_price = []
                                        hold_price.append(cost / (1 - fee))
                                        low_price.append(cost / (1 - fee))
                                        low_price.append(_row.low)
                                        net = net1 * net2 * net
                                        short_stop = False
                                        long_stop = False
                                    elif condition_sp:
                                        s_price = _row.open * (1 - fee)
                                        trad_times += 1
                                        net1 = pos * s_price / _row.close_1 + (1 - pos)
                                        ret = s_price / cost - 1
                                        e_time = _row.date_time
                                        signal_row = []
                                        signal_row.append(symble)
                                        signal_row.append(percentile)
                                        signal_row.append(buy1)
                                        signal_row.append(buy2)
                                        signal_row.append(sell1)
                                        signal_row.append(sell2)
                                        signal_row.append(method_open + '_' + method_close)
                                        signal_row.append(s_time)
                                        signal_row.append(e_time)
                                        signal_row.append(cost)
                                        signal_row.append(s_price)
                                        signal_row.append(ret)
                                        signal_row.append((max(high_price) / cost) - 1)
                                        signal_row.append(len(hold_price))
                                        signal_row.append(pos)
                                        signal_row.append('sp')
                                        signal_lst.append(signal_row)
                                        pos = 0
                                        net = net1 * net
                                        short_stop = False
                                        long_stop = False

                                    else:
                                        high_price.append(_row.high)
                                        hold_price.append(_row.close)
                                        net = net * (pos * _row.close / _row.close_1 + (1 - pos))
                                elif pos < 0:
                                    if condition_bk:
                                        b_price = _row.open * (1 + fee)
                                        e_time = _row.date_time
                                        trad_times += 1
                                        net1 = (1 + pos) - pos * (2 - b_price / _row.close_1)
                                        ret = (cost - b_price) / cost
                                        signal_row = []
                                        signal_row.append(symble)
                                        signal_row.append(percentile)
                                        signal_row.append(buy1)
                                        signal_row.append(buy2)
                                        signal_row.append(sell1)
                                        signal_row.append(sell2)
                                        signal_row.append(method_open + '_' + method_close)
                                        signal_row.append(s_time)
                                        signal_row.append(e_time)
                                        signal_row.append(cost)
                                        signal_row.append(b_price)
                                        signal_row.append(ret)
                                        signal_row.append((cost - min(low_price)) / cost)
                                        signal_row.append(len(hold_price))
                                        signal_row.append(pos)
                                        signal_row.append('bpk')
                                        signal_lst.append(signal_row)
                                        pos = 1
                                        cost = b_price
                                        net2 = pos * _row.close / cost + 1 - pos
                                        s_time = _row.date_time
                                        hold_price = []
                                        high_price = []
                                        hold_price.append(cost / (1 + fee))
                                        high_price.append(cost / (1 + fee))
                                        high_price.append(_row.high)
                                        net = net1 * net2 * net
                                        short_stop = False
                                        long_stop = False
                                    elif condition_bp:
                                        b_price = _row.open * (1 + fee)
                                        e_time = _row.date_time
                                        trad_times += 1
                                        net1 = (1 + pos) - pos * (2 - b_price / _row.close_1)
                                        ret = (cost - b_price) / cost
                                        signal_row = []
                                        signal_row.append(symble)
                                        signal_row.append(percentile)
                                        signal_row.append(buy1)
                                        signal_row.append(buy2)
                                        signal_row.append(sell1)
                                        signal_row.append(sell2)
                                        signal_row.append(method_open + '_' + method_close)
                                        signal_row.append(s_time)
                                        signal_row.append(e_time)
                                        signal_row.append(cost)
                                        signal_row.append(b_price)
                                        signal_row.append(ret)
                                        signal_row.append((cost - min(low_price)) / cost)
                                        signal_row.append(len(hold_price))
                                        signal_row.append(pos)
                                        signal_row.append('bp')
                                        signal_lst.append(signal_row)
                                        pos = 0
                                        net = net1 * net
                                        short_stop = False
                                        long_stop = False


                                    else:
                                        low_price.append(_row.low)
                                        hold_price.append(_row.close)
                                        net = net * ((1 + pos) - pos * (2 - _row.close / _row.close_1))
                                net_lst.append(net)
                                pos_lst.append(pos)
                            net_df_all = pd.DataFrame({'net': net_lst,
                                                       'date_time': group_.date_time.tolist(),
                                                       'close': group_.close.tolist(),
                                                       'pos': pos_lst})
                            signal_state_all = pd.DataFrame(signal_lst, columns=[
                                'symble', 'percentile', 'buy1', 'buy2', 'sell1', 'sell2', 'method', 's_time', 'e_time',
                                'b_price', 's_price', 'ret', 'max_ret', 'hold_day', 'position', 'bspk'])
                            signal_state_all_lst.append(signal_state_all)
                            # signal_state.to_csv('cl_trend/data/signal_gzw_' + str(n) + '_' + symble + '_' + back_stime + 'ls.csv')
                            # df_lst.append(signal_state_all)
                            try:

                                for (s_date, e_date) in date_lst:
                                    net_df = net_df_all[
                                        (net_df_all['date_time'] >= s_date) & (net_df_all['date_time'] <= e_date)]
                                    if len(net_df) < 20:
                                        continue
                                    net_df = net_df.reset_index(drop=True).assign(
                                        close=lambda df: df.close / df.close.tolist()[0]).assign(
                                        net=lambda df: df.net / df.net.tolist()[0])
                                    net_lst_ = net_df.net.tolist()
                                    print('adj%s_%s_%s_%s_%s_%s_%s_%s.csv' % (
                                        index_code, method_open, method_close, buy1, buy2, sell1, sell2,
                                        int(10 * percentile)))
                                    net_df.to_csv(fold + 'net/adj%s_%s_%s_%s_%s_%s_%s_%s.csv' % (
                                        index_code, method_open, method_close, buy1, buy2, sell1, sell2,
                                        int(10 * percentile)))
                                    # net_df[['date_time', 'net', 'close']].plot(
                                    #     x='date_time', kind='line', grid=True,
                                    #     title=symble + '_' + period)
                                    # title = symble[:6] + '_' + method_open + '_' + method_close
                                    # plt.title(title + '.csv')
                                    # plt.savefig(fold + 'fig/' + title + '.png')
                                    # plt.show()
                                    signal_state = signal_state_all[
                                        (signal_state_all['s_time'] >= s_date) & (
                                                signal_state_all['s_time'] <= e_date)]

                                    back_stime = net_df.at[0, 'date_time']
                                    back_etime = net_df.at[len(net_df) - 1, 'date_time']

                                    ann_ROR = annROR(net_lst_, n)
                                    total_ret = net_lst_[-1]
                                    max_retrace = maxRetrace(net_lst_, n)
                                    sharp = yearsharpRatio(net_lst_, n)

                                    win_r, odds, ave_r, mid_r = get_winR_odds(signal_state.ret.tolist())
                                    win_R_3, win_R_5, ave_max = get_winR_max(signal_state.max_ret.tolist())
                                    state_row = []
                                    state_row.append(symble)
                                    state_row.append(n)
                                    state_row.append(win_r)
                                    state_row.append(odds)
                                    state_row.append(total_ret - 1)
                                    state_row.append(ann_ROR)
                                    state_row.append(sharp)
                                    state_row.append(max_retrace)
                                    state_row.append(len(signal_state))
                                    state_row.append(ave_r)
                                    state_row.append(signal_state.hold_day.mean())
                                    state_row.append(win_R_3)
                                    state_row.append(win_R_5)
                                    state_row.append(ave_max)
                                    state_row.append(percentile)
                                    state_row.append(buy1)
                                    state_row.append(buy2)
                                    state_row.append(sell1)
                                    state_row.append(sell2)
                                    state_row.append(method_open + '_' + method_close)
                                    state_row.append(back_stime)
                                    state_row.append(back_etime)
                                    state_lst.append(state_row)
                            except Exception as e:
                                print(str(e))
                                continue
        except Exception as e:
            print(str(e))
            continue

    signal_state = pd.DataFrame(state_lst, columns=['symble', 'tm', 'win_r', 'odds', 'total_ret', 'ann_ret', 'sharp',
                                                    'max_retrace', 'trade_times', 'ave_r', 'ave_hold_days', 'win_r_3',
                                                    'win_r_5', 'ave_max', 'percentile', 'buy1', 'buy2', 'sell1',
                                                    'sell2', 'method',
                                                    's_time', 'e_time'])
    print(signal_state)
    signal_state.to_csv(fold + 'state_kdj_macd_future_' + str(x) + 'adj.csv')
    signal_state_all_df = pd.concat(signal_state_all_lst)
    signal_state_all_df.to_csv(fold + 'signal_kdj_macd_future_' + str(x) + 'adj.csv')