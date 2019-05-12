from lightning import LightningRpc, RpcError
import random
import sys
import os
import math
from pathlib import Path


home = str(Path.home())
lnd = LightningRpc(home+"/.lightning/lightning-rpc")


def lnd_full_info():
    info = lnd.getinfo()
    funds = lnd.listfunds()

    onchain = 0
    offchain = 0
    channel_size = 0
    chan_count = 0

    max_out = 0
    max_in = 0

    total_in = 0
    total_out = 0

    chan_cap = list()
    chan_cap_free = list()

    for out in funds['outputs']:
        #  print(out)
        onchain = onchain + out['value']

    for chan in funds['channels']:
        #print(chan)
        chan_count += 1
        total_out += chan['channel_sat']

        if chan['channel_sat'] > max_out:
            max_out = chan['channel_sat']

        channel_in = chan['channel_total_sat'] - chan['channel_sat']
        chan_cap_free.append(channel_in)
        chan_cap.append(chan['channel_total_sat'])

        total_in += channel_in
        if channel_in > max_in:
            max_in = channel_in
        offchain = offchain + chan['channel_sat']
        channel_size = channel_size + chan['channel_total_sat']
        
    collected_fees = int(str(info['fees_collected_msat']).replace('msat', ''))

    zbx = {
        'onchain': onchain,
        'offchain': offchain,
        'channels': chan_count,
        'total_size': channel_size,
        'fees_collected_msat': collected_fees,
        'avg_chan_cap': int(sum(chan_cap) / len(chan_cap)),
        'avg_chan_free': int(sum(chan_cap_free) / len(chan_cap_free)),
        'max_in': max_in,
        'max_out': max_out
    }

    return zbx



def lnd_count_forwards():
    forwards = lnd.listforwards()['forwards']

    fail_fw_count = 0
    sett_fw_count = 0
    fw_count = 0

    forwards_fees_msat = list()
    forwards_amounts_msat = list()

    for forward in forwards:
        fw_count += 1
        if forward['status'] == 'settled':
            sett_fw_count += 1
            forwards_fees_msat.append(forward['fee'])
            forwards_amounts_msat.append(forward['out_msatoshi'])

        else:
            fail_fw_count += 1

    data = {
        'total_fees': sum(forwards_fees_msat),
        'avg_fee': int(sum(forwards_fees_msat)/len(forwards_fees_msat)),
        'total_forwards_count': fw_count,
        'settled': sett_fw_count,
        'failed': fail_fw_count,
        'avg_amount': int(sum(forwards_amounts_msat)/len(forwards_amounts_msat)),
        'total_amount': sum(forwards_amounts_msat)
    }

    return data

def lnd_paydata():
    pays = lnd.listpays()['pays']

    invoices = lnd.listinvoices()['invoices']

    pays_amounts = list()
    inv_amounts = list()

    for pay in pays:
        if pay['status'] == 'complete':
            payamount = int(float(str(pay['amount_sent_msat']).replace('msat', ''))/1000)
            pays_amounts.append(payamount)

    for inv in invoices:
        if inv['status'] == 'paid':
            amount = int(float(str(inv['msatoshi_received']).replace('msat', ''))/1000)
            inv_amounts.append(amount)


    data = {
        'avg_pay_amount': int(sum(pays_amounts)/len(pays_amounts)),
        'avg_inv_amount': int(sum(inv_amounts)/len(pays_amounts))
    }

    return data


full = lnd_full_info()
fw = lnd_count_forwards()
payinv = lnd_paydata()


for key in full:
    os.system("echo '" + str(full[key]) + "' > /tmp/" + key)

for key in fw:
    os.system("echo '" + str(fw[key]) + "' > /tmp/" + key)

for key in payinv:
    os.system("echo '" + str(payinv[key]) + "' > /tmp/" + key)

