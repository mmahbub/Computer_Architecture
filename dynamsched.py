#!/usr/bin/env python

import os
import sys
import math
from pathlib import Path
import argparse
from collections import defaultdict 
from itertools import groupby

class Dictlist(dict):
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)

"""
Class for storing pipeline configuration information
"""
class Config:
    def __init__(self, file_name):
        self.file_name = file_name # instance variable for file_name
        self.read_config()
        self.print_config()

    # function to read the config values from the given input file_name
    # and store these
    def read_config(self):
        i = 0
        for line in open(self.file_name):
            if ":" not in line:
                continue
            value = line.strip().split(":")[1].strip()
            if i is 0:
                self.num_eff_addr = value
            elif i is 1:
                self.num_fp_add = value
            elif i is 2:
                self.num_fp_mul = value
            elif i is 3:
                self.num_int = value
            elif i is 4:
                self.num_reorder = value
            elif i is 5:
                self.len_fp_add = value
            elif i is 6:
                self.len_fp_sub = value
            elif i is 7:
                self.len_fp_mul = value
            elif i is 8:
                self.len_fp_div = value
            i += 1

        assert int(self.num_reorder) <= 10, "too many entries for the reorder buffer"       

    def print_config(self):
        print("Configuration")
        print("-------------")
        print("buffers:")
        print('%12s' % ('eff addr:'), self.num_eff_addr)
        print('%12s' % ('fp adds:'), self.num_fp_add)
        print('%12s' % ('fp muls:'), self.num_fp_mul)
        print('%12s' % ('ints:'), self.num_int)
        print('%12s' % ('reorder:'), self.num_reorder)
        print("\nlatencies:")
        print('%10s' % ('fp add:'), self.len_fp_add)
        print('%10s' % ('fp sub:'), self.len_fp_sub)
        print('%10s' % ('fp mul:'), self.len_fp_mul)
        print('%10s' % ('fp div:'), self.len_fp_div)

"""
Class for storing information related to datatransfer
"""
class DataTransfer:
    def __init__(self, ins, dest, addr, reg, text):
        self.ins = ins
        self.dest = dest
        self.addr = addr
        self.reg = reg
        self.cost = 1
        self.text = text
        self.issues_at = 0
        self.start_executing = 0
        self.end_executing = 0
        self.writes_result = 0
        self.commits = 0
        self.memory_read = 0

        
"""
Class for storing information related to arithmetic op
"""
class Arithmetic:
    def __init__(self, ins, dest, arg1, arg2, text):
        self.ins = ins
        self.dest = dest
        self.arg1 = arg1
        self.arg2 = arg2
        self.cost = 1
        self.text = text
        self.issues_at = 0
        self.start_executing = 0
        self.end_executing = 0
        self.writes_result = 0
        self.commits = 0
        self.memory_read = 0

        
"""
Class for storing information related to floating-point op
"""
class FloatingPoint:
    def __init__(self, ins, dest, arg1, arg2, cost, text):
        self.ins = ins
        self.dest = dest
        self.arg1 = arg1
        self.arg2 = arg2
        self.cost = int(cost)
        self.text = text
        self.issues_at = 0
        self.start_executing = 0
        self.end_executing = 0
        self.writes_result = 0
        self.commits = 0
        self.memory_read = 0
        
        
"""
Class for storing instructions from the input trace file
"""
class Instructions:
    def __init__(self, config, file_name):
        self.file_name = file_name
        self.data = list()
        self.config = config
        self.read_ins()
        
    def read_ins(self):
        for line in open(self.file_name):
            instruction = line.strip()
            value = line.strip().split()
            if value[0] == "flw":
                args = value[1].split(",")
                addr = args[1].split(":")[1]
                reg = args[1].split(":")[0][-3:-1]
                assert 'f' in args[0], instruction + \
                ": instruction has invalid register"
                self.data.append(DataTransfer(value[0], 
                                              args[0], 
                                              addr, 
                                              reg,
                                              line.strip()))
            if value[0] == 'fsw':
                args = value[1].split(",")
                addr = args[1].split(":")[1]
                reg = args[1].split(":")[0][-3:-1]
                assert 'f' in args[0], instruction + \
                ": instruction has invalid register"
                self.data.append(DataTransfer(value[0], 
                                              addr, 
                                              args[0], 
                                              reg,
                                              line.strip()))
            elif value[0] == "lw":
                args = value[1].split(",")
                addr = args[1].split(":")[1]
                reg = args[1].split(":")[0][-3:-1]
                assert 'x' in args[0], instruction + \
                ": instruction has invalid register"
                self.data.append(DataTransfer(value[0], 
                                              args[0], 
                                              addr, 
                                              reg,
                                              line.strip()))
            elif value[0] == "sw":
                args = value[1].split(",")
                addr = args[1].split(":")[1]
                reg = args[1].split(":")[0][-3:-1]
                assert 'x' in args[0], instruction + \
                ": instruction has invalid register"
                self.data.append(DataTransfer(value[0],
                                              addr, 
                                              args[0], 
                                              reg,
                                              line.strip()))
            elif (value[0] == "fadd.s" or
                value[0] == "fsub.s" or
                value[0] == "fmul.s" or
                value[0] == "fdiv.s"):
                ins = value[0]
                args = value[1].split(",")
                assert 'f' in args[0], instruction + \
                ": instruction has invalid register"
                assert 'f' in args[1], instruction + \
                ": instruction has invalid register"
                assert 'f' in args[2], instruction + \
                ": instruction has invalid register"
                cost = 0
                if value[0] == "fadd.s":
                    cost = self.config.len_fp_add
                elif value[0] == "fsub.s":
                    cost = self.config.len_fp_sub
                elif value[0] == "fmul.s":
                    cost = self.config.len_fp_mul
                elif value[0] == "fdiv.s":
                    cost = self.config.len_fp_div
                self.data.append(FloatingPoint(ins, 
                                               args[0],
                                               args[1], 
                                               args[2], 
                                               cost, 
                                               line.strip()))
            elif (value[0] == "add" or
                value[0] == "sub"):
                ins = value[0]
                args = value[1].split(",")
                assert 'x' in args[0], instruction + \
                ": instruction has invalid register"
                assert 'x' in args[1], instruction + \
                ": instruction has invalid register"
                assert 'x' in args[2], instruction + \
                ": instruction has invalid register"
                self.data.append(Arithmetic(ins, 
                                            args[0],
                                            args[1], 
                                            args[2], 
                                            line.strip()))
            elif (value[0] == "beq" or
                value[0] == "bne"):
                ins = value[0]
                args = value[1].split(",")

                self.data.append(Arithmetic(ins, 
                                            args[0],
                                            args[1], 
                                            args[2], 
                                            line.strip()))


"""
Class for storing registers for register status needs
"""
class RegisterStatus:
    def __init__(self, config, ins):
        self.renames = list()
        self.spot_locator = Dictlist()
        self.spot_remover = Dictlist()
        self.res_locator = Dictlist()
        self.config = config
        self.ins = ins

        for i in range(0, int(self.config.num_reorder)+5):
            self.renames.append(-1)
            
    def find_spot(self, reg, iss):
        x = 0 
        for i in self.renames:
            if i == -1:
                self.spot_locator[reg] = x
                self.res_locator[reg, iss] = x
                self.spot_remover[reg] = x
                self.renames[x] = reg
                return x
            x+=1
       
    def remove_spot(self, reg):
        for k, v in self.spot_remover.items():
            if v:
                if k == reg:
                    x = v[0]
                    v.pop(0)
                    self.renames[x] = -1
            
    def check_in(self, reg):
        for k, v in self.spot_locator.items():
            if v:
                if k == reg:
                    return v[-1]
        return False

    def check_in_for_reset(self, reg, iss):
        for k, v in self.res_locator.items():
            if v:
                if (k[0] == reg and k[1] == iss):
                    x = v[0]
                    v.pop(0)
                    return x
        return False

    def print_status(self):
        print("register status")
        print("---------------")
        x = 0
        for i in self.renames:
            if i != - 1:
                print(i+"=#"+str(x)),
            x+=1
        print("")

        
"""
Class for storing reorder buffer entries
"""
class ReorderEntry:
    def __init__(self, num):
        self.num = num
        self.busy = "no"
        self.ins = ""
        self.status = ""
        self.dest = ""
        self.cycles_left = -1
        self.obj = ""
        self.res = ""

    def __str__(self):
        return (("%5d %-04s %-021s %-011s %-011s"
            % (self.num, self.busy, self.ins, self.status, self.dest)))


"""
Class for implementing reorder buffer simulation
"""
class ReorderBuffer:
    def __init__(self, config):
        self.config = config
        self.entries = list()

        for i in range(int(self.config.num_reorder)):
            self.entries.append(ReorderEntry(i+1))

    def print_buffer(self):
        print("                     Reorder buffer")
        print("--------------------------------------------------------")
        print("Entry Busy      Instruction         State    Destination")
        print("----- ---- --------------------- ----------- -----------")
        for i in self.entries:
            print(i)

    def is_open(self):
        for i in self.entries:
            if i.busy == "no":
                return True
        return False

    def add_open(self, ins, num):
        for i in self.entries:
            if i.busy == "no":
                i.busy = "yes"
                i.ins = ins.text
                i.status = "issued"
                if ins.ins != "bne" and ins.ins != "beq":
                    i.dest = ins.dest
                i.cycles_left = ins.cost
                i.obj = ins
                i.res = num
                return True
        return False


"""
Class for storing reservation station entries
"""
class Station:
    def __init__(self, name, t):
        self.type = t
        self.name = name
        self.busy = "no"
        self.op = ""
        self.qj = ""
        self.qk = ""
        self.dest = ""

    def reset(self):
        self.busy = "no"
        self.op = ""
        self.qj = ""
        self.qk = ""
        self.dest = ""

    def __str__(self):
        return ("%s %-04s %-05s #%-02s #%-02s #%-02s" % 
            (self.name, self.busy, self.op, self.qj, self.qk,
                self.dest))


"""
Class for implementing reservation station simulation
"""
class Stations:
    def __init__(self, config, status):
        self.stations = list()
        self.config = config
        self.status = status
        self.setup()

    def setup(self):
        for i in range(int(self.config.num_eff_addr)):
            self.stations.append(Station("effaddr" + str(i+1), "effaddr"))
        for i in range(int(self.config.num_fp_add)):
            self.stations.append(Station("fpadd  " + str(i+1), "fpadd"))
        for i in range(int(self.config.num_fp_mul)):
            self.stations.append(Station("fpmul  " + str(i+1), "fpmul"))
        for i in range(int(self.config.num_int)):
            self.stations.append(Station("int    " + str(i+1), "int"))

    def print_stations(self):
        print("\tReservation stations")
        print("--------------------------------")
        print("  Name   Busy  Op   Qj  Qk  Dest")
        print("-------- ---- ----- --- --- ----")
        for i in self.stations:
            print(i)

    def check_oj(self, reg, num_reg):
        x = 0
        for i in self.stations:
            if i.dest != '':
                if self.status.renames[int(i.dest)] == reg and x != num_reg:
                    return True
            x+=1
        return False

    def find_spot(self, ins, cycle):
        for x in range(len(self.stations)):
            i = self.stations[x]
            if ins.ins == "sub" or ins.ins == "add":
                if i.busy == "no":
                    if i.type == "int":
                        i.busy = "yes"
                        i.op = ins.ins
                        rs = ins.arg1
                        if self.check_oj(rs,x):
                            i.qj = self.status.check_in(rs)
                        rt = ins.arg2
                        if self.check_oj(rt,x):
                            i.qk = self.status.check_in(rt)
                        dest = self.status.find_spot(ins.dest,cycle)
                        i.dest = dest
                        return True, x
                    
            elif ins.ins == "fadd.s" or ins.ins == "fsub.s":
                if i.busy == "no":
                    if i.type == "fpadd":
                        i.busy = "yes"
                        i.op = ins.ins
                        rs = ins.arg1
                        if self.check_oj(rs,x):
                            i.qj = self.status.check_in(rs)
                        rt = ins.arg2
                        if self.check_oj(rt,x):
                            i.qk = self.status.check_in(rt)
                        dest = self.status.find_spot(ins.dest,cycle)
                        i.dest = dest
                        return True, x

            elif ins.ins == "fmul.s" or ins.ins == "fdiv.s":
                if i.busy == "no":
                    if i.type == "fpmul":
                        i.busy = "yes"
                        i.op = ins.ins
                        rs = ins.arg1
                        if self.check_oj(rs,x):
                            i.qj = self.status.check_in(rs)
                        rt = ins.arg2
                        if self.check_oj(rt,x):
                            i.qk = self.status.check_in(rt)
                        dest = self.status.find_spot(ins.dest,cycle)
                        i.dest = dest
                        return True, x

            elif (ins.ins == "fsw" or ins.ins == "flw" or 
                  ins.ins == "sw" or ins.ins == "lw"):
                if i.busy == "no":
                    if i.type == "effaddr":
                        i.busy = "yes"
                        i.op = ins.ins
                        dest = self.status.find_spot(ins.dest,cycle)
                        i.dest = dest
                        if self.check_oj(ins.reg,x):
                            i.qj = self.status.check_in(ins.reg)                        
                        if self.check_oj(ins.addr,x):
                            i.qk = self.status.check_in(ins.addr)
                        return True, x
                    
            elif ins.ins == "beq" or ins.ins == "bne":
                if i.busy == "no":
                    if i.type == "int":
                        i.busy = "yes"
                        i.op = ins.ins
                        rs = ins.dest
                        if self.check_oj(rs,x):
                            i.qj = self.status.check_in(rs)
                        rt = ins.arg1
                        if self.check_oj(rt,x):
                            i.qk = self.status.check_in(rt)
                        return True, x          
        return False, -1


"""
Class for implementatiing the Tomasulo algorithm for dynamic scheduling
"""
class Pipeline:
    def __init__(self, ins, buff, stations, status, v):
        self.ins = ins
        self.buff = buff
        self.stations = stations
        self.status = status
        self.v = v
        self.memaccess = False
        self.write_queue = list()
        self.commit_queue = list()
        self.store_queue = list()
        self.branch_queue = list()
        self.reset_list = list()
        self.read_queue = list()
        self.cycle = 1
        self.reservation_delays = 0
        self.reorder_delays = 0
        self.data_conflicts = 0
        self.true_dependence = 0

        self.do_tomasulo()

    def issue_instruction(self, ins, num):
        self.buff.add_open(ins, num)

    def check_commited(self):
        for i in self.buff.entries:
            if i.busy == "yes":
                return True
        return False

    def start_executing(self):
        for i in self.buff.entries:
            if i.status == "issued":
                station = self.stations.stations[i.res]
                i.obj.start_executing = self.cycle
                if ((i.obj.ins == "fsw" or i.obj.ins == "sw") and
                      station.qj == ""):
                    i.status = "executing"
                    i.cycles_left = i.cycles_left - 1
                elif ((i.obj.ins == "flw" or i.obj.ins == "lw") and
                      station.qj == ""):
                    i.status = "executing"
                    i.cycles_left = i.cycles_left - 1
                else:
                    if station.qj == "" and station.qk == "":
                        i.status = "executing"
                        i.cycles_left = i.cycles_left - 1
                    else:
                        self.true_dependence += 1

    def finish_executing(self):
        for i in self.buff.entries:
            if i.status == "executing":
                if i.cycles_left == 0:
                    i.status = "executed"
                    i.obj.finish_executing = self.cycle
                    if (i.obj.ins == "fsw" or i.obj.ins == "sw"
                        or i.obj.ins == "beq" or i.obj.ins == "bne"):
                        self.commit_queue.append(i)
                        if (i.obj.ins == "fsw" or i.obj.ins == "sw"):
                            self.store_queue.append(i)
                        elif (i.obj.ins == "beq" or i.obj.ins == "bne"):
                            self.branch_queue.append(i)
                    elif i.obj.ins == "flw" or i.obj.ins == "lw":
                        self.read_queue.append(i)
                    else:
                        self.write_queue.append(i)
                         
    def check_store(self, val, count):
        q = []
        for buff in self.buff.entries:
            if buff.busy == 'yes':
                if ((buff.obj.ins == 'flw' and buff.status == 'issued') or 
                    (buff.obj.ins == 'flw' and buff.status == 'executed') or
                    (buff.obj.ins == 'lw' and buff.status == 'issued') or 
                    (buff.obj.ins == 'lw' and buff.status == 'executed')):
                    q.append(buff)
                elif (buff.obj.ins == 'fsw' or buff.obj.ins == 'sw'):
                    q.append(buff)
        q.sort(key= lambda x: x.obj.issues_at)
        ls_add, ls_ins = [], []
        for i in range(len(q)):
            if (q[i].obj.ins == 'fsw' or q[i].obj.ins == 'sw'):
                ls_ins.append(q[i].obj.ins)
                ls_add.append(q[i].obj.dest)
            elif (q[i].obj.ins == 'flw' or q[i].obj.ins == 'lw'): 
                ls_ins.append(q[i].obj.ins)
                ls_add.append(q[i].obj.addr)
                
        d = defaultdict(list)
        for index, e in enumerate(ls_ins):
            d[e].append(index)
        
        if (('flw' in ls_ins or 'lw' in ls_ins) and self.memaccess):
            if count:
                self.data_conflicts += 1
            return False
        
        elif (('fsw' in ls_ins and ls_ins.index('fsw') == 0) or
              ('sw' in ls_ins and ls_ins.index('sw') == 0)):
          
            if ('fsw' in ls_ins and 
                ls_ins.index(val.obj.ins) > ls_ins.index('fsw')):
                sd_in = max(d['fsw']) 
                if (val.obj.addr == ls_add[sd_in]):
                    if count:
                        self.true_dependence += 1
                    return False

            elif ('sw' in ls_ins and 
                  ls_ins.index(val.obj.ins) > ls_ins.index('sw')):
                sd_in = max(d['sw'])         
                if (val.obj.addr == ls_add[sd_in]):
                    if count:
                        self.true_dependence += 1
                    return False
        return True

    def read_stage(self):
        if len(self.read_queue) > 1:
            for i in range(1,len(self.read_queue)):
                if self.read_queue[0].obj.finish_executing == self.read_queue[i].obj.finish_executing:
                    self.data_conflicts += 1
                else:
                    self.true_dependence += 1
                    
        if len(self.read_queue) > 0:
            self.read_queue.sort(key= lambda x: x.obj.issues_at)
            count = True
            for val in self.read_queue:
                if self.check_store(val,count):
                    val.status = "memread"
                    val.obj.memory_read = self.cycle
                    self.write_queue.append(val)
                    self.read_queue.remove(val)  
                count = False
                
    def write_stage(self):
        if len(self.write_queue) > 0:
            self.write_queue.sort(key= lambda x: x.obj.issues_at)
            val = self.write_queue.pop(0)
            val.status = "wroteresult"
            val.obj.writes_result = self.cycle
            dest = self.status.check_in_for_reset(val.dest, val.obj.issues_at)
            self.reset_list.append(dest)
            station = self.stations.stations[val.res]
            station.reset()
            self.commit_queue.append(val)

    def reset_store_branch(self):
        if len(self.store_queue) > 0:
            self.store_queue.sort(key= lambda x: x.obj.issues_at)
            val = self.store_queue.pop(0)
            dest = self.status.check_in_for_reset(val.dest, val.obj.issues_at)
            self.reset_list.append(dest)
            station = self.stations.stations[val.res]
            station.reset()
            
        if len(self.branch_queue) > 0:
            self.branch_queue.sort(key= lambda x: x.obj.issues_at)
            val = self.branch_queue.pop(0)
            dest = self.status.check_in_for_reset(val.dest, val.obj.issues_at)
            self.reset_list.append(dest)
            station = self.stations.stations[val.res]
            station.reset()

    def commit_in_order(self, ins):
        ins_issued = ins.obj.issues_at
        for i in self.buff.entries:
            if i.busy == "yes": 
                if i.obj.issues_at < ins.obj.issues_at:
                    return False
        return True

    def commit_result(self):
        if len(self.commit_queue) > 0:
            self.commit_queue.sort(key= lambda x: x.obj.issues_at)
            if self.commit_in_order(self.commit_queue[0]):
                val = self.commit_queue.pop(0)
                val.status = "committed"
                val.busy = "no"
                val.obj.commits = self.cycle
                if (val.obj.ins == "fsw" or val.obj.ins == "sw"):  
                    self.memaccess = True
                self.status.remove_spot(val.dest)

    def still_executing(self):
        for i in self.buff.entries:
            if i.status == "executing":
                i.cycles_left -= 1

    def resets_for_waiting(self):
        for dest in self.reset_list:
            for i in self.stations.stations:
                if i.qj == dest:
                    i.qj = ""
                if i.qk == dest:
                    i.qk = ""

    def do_tomasulo(self):
        stack = list(self.ins.data)
        first_ins = True
        while self.check_commited() or first_ins:
            first_ins = False
            self.resets_for_waiting()
            if self.reset_list:
                self.reset_list.pop(0)
            self.still_executing()
            self.commit_result()
            self.reset_store_branch()
            self.write_stage()
            self.read_stage()
            self.start_executing()
            self.finish_executing()
            self.memaccess = False

            if len(stack) > 0:
                i = stack[0]
                if (self.buff.is_open()):
                    res, num = self.stations.find_spot(i, self.cycle)
                    if res:
                        self.issue_instruction(i, num)
                        stack.pop(0)
                        i.issues_at = self.cycle
                    else:
                        self.reservation_delays += 1
                else:
                    self.reorder_delays += 1
                    
            if self.v:
                print("\nCycle: " + str(self.cycle))
                print("")
                self.stations.print_stations()
                print("")
                self.buff.print_buffer()
                print("")
                self.status.print_status()

            self.cycle+=1

"""
Class for printing out the final results
"""
class PipelineResults:
    def __init__(self, ins, rob, res, data, true):
        self.ins = ins
        self.rob = rob
        self.res = res
        self.data = data
        self.true = true
        self.setup_header()
        self.print_results()
        self.print_delays()
        
    def setup_header(self):
        print("\n\n                    Pipeline Simulation")
        print("-----------------------------------------------------------")
        print("                                      Memory Writes")
        print("     Instruction      Issues Executes  Read  Result Commits")
        print("--------------------- ------ -------- ------ ------ -------")

    def print_results(self):
        for i in ins.data:
            if i.ins == "flw" or i.ins == "lw":
                print("%-021s %6s %03s -%03s %06s %06s %07s" % 
                    (i.text, 
                        i.issues_at, 
                        i.start_executing, 
                        i.finish_executing,
                        i.memory_read, 
                        i.writes_result, 
                        i.commits))
            
            elif (i.ins == "fsw" or i.ins == "sw" 
                or i.ins == "bne" or i.ins == "beq"):
                    print("%-021s %6s %03s -%03s               %07s" % 
                    (i.text, 
                        i.issues_at, 
                        i.start_executing, 
                        i.finish_executing,
                        i.commits))
            else:
                print("%-021s %6s %03s -%03s        %06s %07s" % 
                    (i.text, 
                        i.issues_at, 
                        i.start_executing, 
                        i.finish_executing,
                        i.writes_result, 
                        i.commits))

    def print_delays(self):
        print("\n\nDelays")
        print("------")
        print("reorder buffer delays:", self.rob)
        print("reservation station delays:", self.res)
        print("data memory conflict delays:", self.data)
        print("true dependence delays:", self.true)
        
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(action='store', dest='config_file', 
                        help='The config file name.')
    parser.add_argument(action='store', dest='trace_data', 
                        help='The trace data file name.')
    parser.add_argument('-v', dest='feature', 
                        action='store_true')

    args = parser.parse_args()
    config_file = args.config_file
    trace_data = args.trace_data
    v = args.feature

    config_file = config_file #'config.txt'
    config = Config(config_file)
    
    trace = trace_data #'trace.dat'
    ins = Instructions(config, trace)
    
    status = RegisterStatus(config, ins) #register status
    res = Stations(config, status) #reservation stations
    buff = ReorderBuffer(config) #reorder buffer
    pipe = Pipeline(ins, buff, res, status, v) #main pipelining
    results = PipelineResults(ins, pipe.reorder_delays, 
                              pipe.reservation_delays,
                              pipe.data_conflicts, 
                              pipe.true_dependence) #final result printing
