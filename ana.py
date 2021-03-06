#! /Users/tianranmao/Projects/so1.0/venv/bin/python

import cmd
import os
import re
import pandas as pd
import numpy as np
from bsm_option_class import call_option, put_option
from datetime import datetime, timedelta
from so_func import get_exercise_time

class Ana(cmd.Cmd):
    intro = 'Welcome to so shell.   Type help or ? to list commands.\n'
    df = None
    r = 0.025
    csv_file = f"./csv/{datetime.today().strftime('%Y-%m-%d')}.csv"
    log_file = f"./log/trade.log"

    def get_K(self, S):
        if S < 3:
            low = '0'+str(int(S*1000 - S * 1000 % 50))
            high = '0'+str(int(S*1000 - S * 1000 % 50 + 50))
            return (low, high)
        elif S > 3:
            low = '0'+str(int(S*1000 - S * 1000 % 100))
            high = '0'+str(int(S*1000 - S * 1000 % 100 + 100))
            return (low, high)
        else:
            low = '03000'
            high = '03000'
            return (low, high)

    def pair_ana(self, UDL, K1, K2):
        EXP = (datetime.now()+timedelta(days=30)).strftime('%y%m')

        T = round((get_exercise_time(EXP[0:2], EXP[2:]) - self.df.index[-1]).total_seconds()/(365*24*3600), 5)

        kc = float(K1[-5:])/1000.0
        kp = float(K2[-5:])/1000.0

        name_c = f'{UDL}C{EXP}M{K1}'
        name_p = f'{UDL}P{EXP}M{K2}'

        self.df = pd.read_csv(self.csv_file, index_col='time', parse_dates=['time'])
        self.df = self.df[[UDL, name_c, name_p]]
        self.df.dropna(axis='index', how='any', inplace=True)

        su = self.df[UDL].iloc[-1]
        
        sc = self.df[name_c].iloc[-1]
        sp = self.df[name_p].iloc[-1]

        oc_real = call_option(su, kc, T, self.r, 0.3)
        op_real =  put_option(su, kp, T, self.r, 0.3)

        ivc = oc_real.imp_vol(sc)
        ivp = op_real.imp_vol(sp)

        if K1==K2:
            ir = np.log(kc/(su+sp-sc))/T
            ir = round(ir, 3)
        else:
            ir = '-'

        oc_delta_1p = call_option(su*1.01, kc, T, self.r, ivc)
        op_delta_1p =  put_option(su*1.01, kp, T, self.r, ivp)
        oc_delta_1m = call_option(su*0.99, kc, T, self.r, ivc)
        op_delta_1m =  put_option(su*0.99, kp, T, self.r, ivp)
        oc_delta_2p = call_option(su*1.02, kc, T, self.r, ivc)
        op_delta_2p =  put_option(su*1.02, kp, T, self.r, ivp)
        oc_delta_2m = call_option(su*0.98, kc, T, self.r, ivc)
        op_delta_2m =  put_option(su*0.98, kp, T, self.r, ivp)
        oc_delta_3p = call_option(su*1.03, kc, T, self.r, ivc)
        op_delta_3p =  put_option(su*1.03, kp, T, self.r, ivp)
        oc_delta_3m = call_option(su*0.97, kc, T, self.r, ivc)
        op_delta_3m =  put_option(su*0.97, kp, T, self.r, ivp)

        oc_vega_m = call_option(su, kc, T, self.r, ivc-0.01)
        op_vega_m =  put_option(su, kp, T, self.r, ivp-0.01)

        delta_1p = oc_delta_1p.value() + op_delta_1p.value() - sc - sp
        delta_1m = oc_delta_1m.value() + op_delta_1m.value() - sc - sp
        delta_2p = oc_delta_2p.value() + op_delta_2p.value() - sc - sp
        delta_2m = oc_delta_2m.value() + op_delta_2m.value() - sc - sp
        delta_3p = oc_delta_3p.value() + op_delta_3p.value() - sc - sp
        delta_3m = oc_delta_3m.value() + op_delta_3m.value() - sc - sp
        vega_m = oc_vega_m.value() + op_vega_m.value() - sc - sp

        print(f"{' ':>8}{UDL}{' ':>22}{name_c} + {name_p} {' ':15}{self.df.index[-1]}")
        print(f"{' ':>8}{'-'*148}")
        print(f"{' ':>8}{'C':>8}{'P':>8}{'S':>8}{'KC':>8}{'KP':>8}{'ivc':>8}{'ivp':>8}{'ir':>8}{' ':15}{'---':^10}{'--':^10}{'-':^10}{'vega':^10}{'+':^10}{'++':^10}{'+++':^10}")
        print(f"{' ':>8}{round(sc,4):>8}{round(sp,4):>8}{round(su,3):>8}{kc:>8}{kp:>8}{round(ivc,3):>8}{round(ivp,3):>8}{ir:>8}{' ':15}{round(delta_3m,4):^10}{round(delta_2m,4):^10}{round(delta_1m,4):^10}{round(vega_m,4):^10}{round(delta_1p,4):^10}{round(delta_2p,4):^10}{round(delta_3p,4):^10}")
        print('\n')

    def do_run(self, arg):
        self.df = pd.read_csv(self.csv_file, index_col='time', parse_dates=['time'])
        self.df = self.df[['510300', '510050']]
        self.df.dropna(axis='index', how='any', inplace=True)
        if arg=='50':
            kl, kh = self.get_K(self.df['510050'].iloc[-1])
            self.pair_ana('510050', kl, kl)
            self.pair_ana('510050', kl, kh)
            self.pair_ana('510050', kh, kl)
            self.pair_ana('510050', kh, kh)

        elif arg=='300':
            kl, kh = self.get_K(self.df['510300'].iloc[-1])
            self.pair_ana('510300', kl, kl)
            self.pair_ana('510300', kl, kh)
            self.pair_ana('510300', kh, kl)
            self.pair_ana('510300', kh, kh)

        else:
            print('Usage: run 50/300')
        print()

    def help_run(self):
        print('Run a monitor on option(50/300) markets.')
        print('Usage: run 50/300')
        print()

    def do_pft(self, arg):
        self.df = pd.read_csv(self.csv_file, index_col='time', parse_dates=['time'])
        self.df.dropna(inplace=True)
        pattern_trade = re.compile(r'^(BUY|SELL)\s+(\w+)\s+@\s+([.\d]+)\s+x\s+([\d]+)')

        PROF = {}
        BUY = {}
        SELL = {}
        COMBS = []

        with open(self.log_file, 'r') as rf:
            for line in rf:
                if line.split() == []:
                    COMBS.append((BUY, SELL))
                    BUY = {}
                    SELL = {}
                else:
                    match_trade = re.search(pattern_trade, line)
                    op = match_trade.group(1)
                    code = match_trade.group(2)
                    price = float(match_trade.group(3))
                    volume = int(match_trade.group(4))
                    if op == 'BUY':
                        BUY.update({code:[price, volume, 'done']})
                    elif op =='SELL':
                        SELL.update({code:[price, volume, 'done']})
            COMBS.append((BUY, SELL))

        for BUY, SELL in COMBS:
            for code in BUY:
                if code not in SELL:
                    if code[6] == 'C':
                        SELL.update({code: [self.df[code][-1], BUY[code][1], 'to be']})
                    else:
                        SELL.update({code: [self.df[code][-1], BUY[code][1], 'to be']})

            for code in SELL:
                if code not in BUY:
                    if code[6] == 'C':
                        BUY.update({code: [self.df[code][-1], SELL[code][1], 'to be']})
                    else:
                        BUY.update({code: [self.df[code][-1], SELL[code][1], 'to be']})

        for BUY, SELL in COMBS:
            print(f'{self.df.index[-1]}', end='')
            for k in sorted(BUY.keys()):
                print(f'{k: >19}', end='')
            print(f'{"TOTAL": >19}', end='')
            print()

            print(f"{'BUY@':>19}", end='')
            for k in sorted(BUY.keys()):
                if BUY[k][2] == 'done':
                    print(f'{BUY[k][0]: >19}', end='')
                else:
                    print(f'{"*"+str(BUY[k][0]): >19}', end='')
            print()

            print(f"{'SELL@': >19}", end='')
            for k in sorted(BUY.keys()):
                if SELL[k][2] == 'done':
                    print(f'{SELL[k][0]: >19}', end='')
                else:
                    print(f'{"*"+str(SELL[k][0]): >19}', end='')
            print()

            print(f"{'PROFITS':>19}", end='')
            tt = 0
            for k in sorted(BUY.keys()):
                tt += round(SELL[k][0]-BUY[k][0],4)
                print(f'{round(SELL[k][0] - BUY[k][0],4): >19}', end='')

            print(f'{round(tt,4): >19}')
            print()

    def help_pft(self):
        print("Calculate the profits for you, which hopefully are positive. :)")
        print('')
        return True

    def do_exit(self, arg):
        print("Thank you. Bye.")
        print('')
        return True

    def help_exit(self):
        print('Quit program.')
        print('')

if __name__ == '__main__':
    Ana().cmdloop()
