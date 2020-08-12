#!/usr/local/bin/python
# -*- coding: utf-8 -*-

'''
we will be working with similar main, you should not change this file!
all your imports/constants/classes/func should be held in hw2_students.py
'''

from hw2_part1 import *


def main_A():
    ############################
    # Question 1
    ############################
    block_size = 102400
    current_time = 1510264253.0

    mempool_data_name = 'bitcoin_mempool_data.csv'
    mempool_data_full_path = os.path.abspath(mempool_data_name)
    all_mempool_data = pd.read_csv(mempool_data_full_path)
    all_pending_transactions = filter_mempool_data(all_mempool_data,current_time)
    tx_to_insert_list = greedy_knapsack(block_size, all_pending_transactions)
    print(len(tx_to_insert_list))
    evaluated_block = evaluate_block(tx_to_insert_list, all_pending_transactions)
    print('pay-your-bid revenue: ', evaluate_block(tx_to_insert_list, all_pending_transactions))
    vcg = VCG_prices(block_size, tx_to_insert_list, all_pending_transactions)
    #
    # block_times = blocks_by_time_1510266000()
    # print(len(block_times))
    # print(block_times)
    #
    #
    # block_times = blocks_after_time_1510266000()
    # print(len(block_times))
    # print(block_times)

    print('vcg revenue: ', sum(vcg.values()))
    print(vcg.values())

def main_B():
    ############################
    # Question 2 + competitive part
    ############################
    block_size = 75000
    time_begin_lin = 180
    time_end_lin = 900

    mempool_data_name = 'bitcoin_mempool_data.csv'
    mempool_data_full_path = os.path.abspath(mempool_data_name)
    all_mempool_data = pd.read_csv(mempool_data_full_path)

    my_TXs_full_path = 'TX_data.csv'
    my_TXs = load_my_TXs(my_TXs_full_path)

    simpleAgent = SimpleBiddingAgent(time_begin_lin,time_end_lin,block_size)
    forwardAgent = ForwardBiddingAgent(time_begin_lin,time_end_lin,block_size)
    competitiveAgent = CompetitiveBiddingAgent(time_begin_lin,time_end_lin,block_size)
    #
    counter = 0
    utility_list = list()
    bid = list()
    time_list = list()
    tx_num = list()
    competitive_bid_list = list()
    for index,TX in my_TXs.iterrows():
        TX_min_value = TX.min_value
        TX_max_value = TX.max_value
        TX_Size = TX.Size
        current_time = TX.time
        counter +=1
        current_mempool_data =  filter_mempool_data(all_mempool_data,current_time)
        simple_bid = simpleAgent.bid(TX_min_value, TX_max_value, TX_Size, current_mempool_data, current_time)
        forward_bid, predicted_time, predicted_utility = forwardAgent.bid(TX_min_value, TX_max_value, TX_Size, current_mempool_data, current_time)
        tx_num.append(counter)
        time_list.append(predicted_time)
        bid.append(forward_bid)
        utility_list.append(predicted_utility)
        competitive_bid = competitiveAgent.bid(TX_min_value, TX_max_value, TX_Size, current_mempool_data, current_time)
        competitive_bid_list.append(competitive_bid)
    ######################################################## exporting the information to CSV files ##################
    write_file_ForwardAgent(tx_num,time_list,bid,utility_list)
    write_file_CompetitiveAgent(tx_num,competitive_bid_list)



if __name__ == "__main__":
    main_A()
    main_B()