############################
# Insert your imports here
import os
import pandas as pd
import csv


############## filtering data by current time, return as a dataframe #################
def filter_mempool_data(mempool_data,current_time):
    mempool_data=mempool_data.loc[(mempool_data['time']<current_time)&(mempool_data['removed']>current_time)]
    return mempool_data

############## creating a list of transactions that entered the block #################
def greedy_knapsack(block_size, all_pending_transactions):
    fee_per_byte=all_pending_transactions['fee'] / all_pending_transactions['size']
    sorted = all_pending_transactions.assign(f=fee_per_byte).sort_values('f', ascending=[0]).drop('f',axis=1)
    tx_list = []
    min_size = sorted['size'].min()
    for index, row in sorted.iterrows():
        if block_size < min_size:
            break
        if row['size'] < block_size:
            tx_list.append(row['TXID'])
            block_size = block_size - row['size']

    return tx_list

def evaluate_block(tx_list, all_pending_transactions):
    r = 0
    for id in tx_list:
        r += all_pending_transactions[all_pending_transactions['TXID'] == id]['fee'].values
    return r[0]


# return a dict of tx_id as keys, for each tx_id its VCG price in satoshi]
def VCG_prices(block_size, tx_list, all_pending_transactions):
    #takes 2 minutes
    vcg = {}
    V_tx_without_i={}
    V_tx_excluding_i={}
    fees={}
    for id in tx_list:
        for txid in range(all_pending_transactions.shape[0]):
            if id==all_pending_transactions.iloc[txid,0]:
                fees[all_pending_transactions.iloc[txid,0]]=all_pending_transactions.iloc[txid,1]
    revenue = evaluate_block(tx_list, all_pending_transactions)
    for tx in tx_list:
        apt_i=all_pending_transactions[all_pending_transactions.TXID != tx]
        tx_list_i=greedy_knapsack(block_size,apt_i)
        r_i=evaluate_block(tx_list_i,apt_i)
        V_tx_without_i[tx]=r_i
        V_tx_excluding_i[tx]=revenue-fees[tx]
        vcg[tx]=V_tx_without_i[tx]-V_tx_excluding_i[tx]

    return vcg

def blocks_after_time_1510266000():
    # all_mempool_data = all_mempool_data[all_mempool_data.time < 1510266000]
    # all_mempool_data = all_mempool_data[all_mempool_data.removed > 1510266000]
    # removed_times = all_mempool_data['removed']
    # unique_times = removed_times.unique()
    # unique_times.sort()
    # return list(unique_times)[0:10]
    return [1510266190, 1510266490, 1510267250, 1510267730, 1510267834,
    1510268791, 1510269386, 1510269627, 1510270136, 1510270686]

def blocks_by_time_1510266000():
    return [1510261800,
            1510262800,
            1510263100,
            1510264600,
            1510264700,
            1510265400,
            1510265600,
            1510265900,
            1510266200,
            1510266500]

#PART B#
def load_my_TXs(my_TXs_full_path):
    my_tx = pd.read_csv(my_TXs_full_path)
    return my_tx

class BiddingAgent:
    def __init__(self, time_begin_lin, time_end_lin, block_size):
        self.time_begin_lin = time_begin_lin
        self.time_end_lin = time_end_lin
        self.block_size = block_size

class SimpleBiddingAgent(BiddingAgent):
    def bid(self, TX_min_value, TX_max_value, TX_size, current_mempool_data, current_time):
        mid_value = (TX_min_value + TX_max_value) / 2
        bid = mid_value
        if TX_size > 1000:
            bid = bid * 1.2
        return bid
class ForwardBiddingAgent(BiddingAgent):

    def bid(self, TX_min_value, TX_max_value, TX_size, current_mempool_data, current_time):
        #takes 21 minutes
        ## IMPLEMENT for Forward_agent part ##
        t_min=self.time_begin_lin
        t_max=self.time_end_lin
        block_size=self.block_size

        fee_per_byte = current_mempool_data['fee'] / current_mempool_data['size']
        cmd_with_fpb = current_mempool_data.assign(f=fee_per_byte)
        blocks={}
        i=0
        while cmd_with_fpb.empty==False and i<=t_max/60:
            tx_list=greedy_knapsack(block_size,cmd_with_fpb)
            blocks[i]=list()
            for id in tx_list:
                blocks[i].append(cmd_with_fpb[cmd_with_fpb['TXID'] == id]['f'].values[0])
                cmd_with_fpb= cmd_with_fpb[cmd_with_fpb['TXID'] != id]
            i+=1

        t_z={}
        #calculate t(z)
        for z in range(5, 1000, 5):
            for i in blocks.keys():
                if min(blocks[i])<=z:
                    t_z[z]=i*60
                    break

        dict_fee={}
        dict_time={}
        dict_gu={}
        for z in t_z.keys():
            value = 0
            if (t_z[z]<t_min):
                value=TX_max_value
            elif t_z[z]>=t_min and t_z[z]<t_max:
                value=TX_max_value-(((TX_max_value-TX_min_value)/(t_max-t_min))*(t_z[z]-t_min))
            elif t_z[z]>=t_max:
                value=0

            #calculate fee
            if TX_size<block_size:
                fee_z = z * TX_size
            else:
                fee_z=0

            #calculate GU
            GU=value-fee_z
            dict_fee[z]=fee_z
            dict_time[z]=t_z[z]
            dict_gu[z]=GU

        #check for max GU
        max_GU = max(dict_gu, key=dict_gu.get)
        bid_best_z = dict_fee[max_GU]
        time_if_z = dict_time[max_GU]
        utility_if_z = dict_gu[max_GU]

        if utility_if_z<=0:
            utility_if_z=0
            bid_best_z=-1
            time_if_z=-1

        return bid_best_z, time_if_z, utility_if_z



class CompetitiveBiddingAgent(BiddingAgent):
    def bid(self, TX_min_value, TX_max_value, TX_size, current_mempool_data, current_time):
        ## IMPLEMENT for competitive part ##
        #print("competitive starting")
        t_min = self.time_begin_lin
        t_max = self.time_end_lin
        block_size = self.block_size
        t0 = 1510262000
        t_star = 1510268001
        fee_per_byte = current_mempool_data['fee'] / current_mempool_data['size']
        mempool_data = current_mempool_data.loc[
            ((current_mempool_data['time'] >= t0) & (current_mempool_data['time'] <= t_star))
            | ((current_mempool_data['time'] <= t0) &
                                            (current_mempool_data['removed'] - current_mempool_data['time'] < 1800))]

        cmd_with_fpb = mempool_data.assign(f=fee_per_byte).drop('removed', axis=1)
        blocks = {}
        block_i_size={}
        i = 0
        while cmd_with_fpb.empty == False and i <= t_max / 60:
            tx_list = greedy_knapsack(block_size, cmd_with_fpb)
            blocks[i] = list()
            sum=0
            for id in tx_list:
                sum+=cmd_with_fpb[cmd_with_fpb['TXID'] == id]['size'].values[0]
                blocks[i].append(cmd_with_fpb[cmd_with_fpb['TXID'] == id]['f'].values[0])
                cmd_with_fpb = cmd_with_fpb[cmd_with_fpb['TXID'] != id]
            block_i_size[i]=sum
            i += 1

        t_z = {}
        # calculate t(z)
        for z in range(5, 1000):
            for i in blocks.keys():
                if TX_size+block_i_size[i]<=block_size:
                    t_z[z]=i*60
                    break
                elif min(blocks[i]) <= z:
                    t_z[z] = i * 60
                    break

        dict_fee = {}
        dict_gu = {}
        for z in t_z.keys():
            value = 0
            if (t_z[z] < t_min):
                value = TX_max_value
            elif t_z[z] >= t_min and t_z[z] < t_max:
                value = TX_max_value - (((TX_max_value - TX_min_value) / (t_max - t_min)) * (t_z[z] - t_min))
            elif t_z[z] >= t_max:
                value = 0

            # calculate fee
            if TX_size < block_size:
                fee_z = z * TX_size
            else:
                fee_z = 0

            # calculate GU
            GU = value - fee_z
            dict_fee[z] = fee_z
            dict_gu[z] = GU

        # check for max GU
        max_GU = max(dict_gu, key=dict_gu.get)
        fee_comp = dict_fee[max_GU]
        GU_comp = dict_gu[max_GU]

        if GU_comp <= 0:
            GU_comp = 0
            fee_comp = 0

        min_val = TX_min_value
        max_val = TX_max_value
        tx_size = TX_size
        curr_time = current_time
        curr_mempool=current_mempool_data

        forwardAgent = ForwardBiddingAgent(t_min, t_max, block_size)
        fee_forward, t_forward, GU_forward = forwardAgent.bid(min_val, max_val, tx_size, curr_mempool, curr_time)
        if GU_comp < GU_forward:
            fee_comp = fee_forward
        if fee_comp == -1:
            fee_comp = 0

        bid_competitive=fee_comp
        return bid_competitive

def write_file_ForwardAgent(tx_num,time_list,bid,utility_list):
    """writing lists to a csv files"""
    filename = 'hw2_ForwardAgent.csv'
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        fieldnames2 = ["Index","Time", "Bid", "Utility"]
        writer.writerow(fieldnames2)
        for i in range(len(utility_list)):
            writer.writerow([tx_num[i],time_list[i], bid[i], utility_list[i]])
def write_file_CompetitiveAgent(tx_num,competitive_bid):
    """writing lists to a csv files"""
    filename = 'hw2_CompetitiveAgent.csv'
    with open(filename, 'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        fieldnames2 = ["Index","Bid"]
        writer.writerow(fieldnames2)
        for i in range(len(competitive_bid)):
            writer.writerow([tx_num[i],competitive_bid[i]])