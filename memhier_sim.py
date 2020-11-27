#!/usr/bin/env python

import os
import sys
import math
from pathlib import Path
import argparse
import glob
import logging
import logging.handlers

"""
Class for printing config file
"""
class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        # initiate data TLB config
        self.index_dtlb = 0
        self.num_sets_dtlb = 0
        self.set_size_dtlb = 0
        # initiate page table config
        self.index_pt = 0
        self.offset_pt = 0
        self.num_virtual_pg = 0
        self.num_physical_pg = 0
        self.page_size = 0
        # initiate data cache config
        self.index_datacache = 0 
        self.offset_datacache = 0
        self.num_sets_datacache = 0
        self.set_size_datacache = 0
        self.line_size_datacache = 0
        # initiate l2 cache config
        self.index_l2cache = 0
        self.offset_l2cache = 0
        self.num_sets_l2cache = 0
        self.set_size_l2cache = 0
        self.line_size_l2cache = 0
        # initiate flags
        self.write_back_datacache = False
        self.write_back_l2cache = False
        self.virtual_address = False
        self.tlb = False
        self.l2_cache = False
        self.read_config()

        # calculate index and offsets for perspective values
        self.calculate_values()

        # print the config file
        self.print_config()
        self.print_header()
        
    def read_config(self):
        # counter 
        i = 0
        # read config file
        for line in open(self.config_file):
            if ":" not in line:
                continue
                
            value = line.strip().split(":")[1].strip()
            if i is 0:
                self.num_sets_dtlb = int(value)
                assert self.num_sets_dtlb <= 256, \
                "The maximum number of sets for the DTLB is 256."
                assert math.log(self.num_sets_dtlb, 2).is_integer(), \
                "Number of sets has to be power of 2."
            elif i is 1:
                self.set_size_dtlb = int(value)
                assert self.set_size_dtlb <= 8, \
                "The maximum associativity level for DTLB is 8."
            elif i is 2:
                self.num_virtual_pg = int(value)
                assert self.num_virtual_pg <= 8192, \
                "The maximum number of virtual pages is 8192."
                assert math.log(self.num_virtual_pg, 2).is_integer(), \
                "Number of virtual pages has to be power of 2."
            elif i is 3:
                self.num_physical_pg = int(value)
                assert self.num_physical_pg <= 1024, \
                "The maximum number of physical pages is 1024."
            elif i is 4:
                self.page_size = int(value)
                assert math.log(self.page_size, 2).is_integer(), \
                "Page size has to be power of 2."
            elif i is 5:
                self.num_sets_datacache = int(value)
                assert self.num_sets_datacache <= 8192, \
                "The maximum number of sets for the DC is 8192."
                assert math.log(self.num_sets_datacache, 2).is_integer(), \
                "Number of sets has to be power of 2."
            elif i is 6:
                self.set_size_datacache = int(value)
                assert self.set_size_datacache <= 8, \
                "The maximum associativity level for DC is 8"
            elif i is 7:
                self.line_size_datacache = int(value)
                assert self.line_size_datacache >= 8, \
                "The data line size for the DC should be at least 8."
                assert math.log(self.line_size_datacache, 2).is_integer(), \
                "Line size has to be power of 2."
            elif i is 8:
                if value is "n":
                    self.write_back_datacache = True 
                else:
                    self.write_back_datacache = False
            elif i is 9:
                self.num_sets_l2cache = int(value)
            elif i is 10:
                self.set_size_l2cache = int(value)
                assert self.set_size_l2cache <= 8, \
                "The maximum associativity level for L2 is 8"
            elif i is 11:
                self.line_size_l2cache = int(value)
                assert self.line_size_l2cache >= self.line_size_datacache, \
                "The data line size for the L2 should be greater than or \
                equal to that of the DC."
                assert math.log(self.line_size_l2cache, 2).is_integer(), \
                "Line size has to be power of 2."
            elif i is 12:
                if value is "n":
                    self.write_back_l2cache = True
                else:
                    self.write_back_l2cache = False
            elif i is 13:
                if value is "n":
                    self.virtual_address = False
                else:
                    self.virtual_address = True
            elif i is 14:
                if value is "n":
                    self.tlb = False
                else:
                    self.tlb = True
            elif i is 15:
                if value is "n":
                    self.l2_cache = False
                else:
                    self.l2_cache = True 
            # increase counter      
            i += 1


    def calculate_values(self):
        # data-cache calculations
        self.index_datacache = int(math.log(float(self.num_sets_datacache), 2))
        self.offset_datacache = int(math.log(float(self.line_size_datacache), 2))
        
        # l2-cache calculations
        self.index_l2cache = int(math.log(float(self.num_sets_l2cache), 2))
        self.offset_l2cache = int(math.log(float(self.line_size_l2cache), 2))

        # data-tlb calculations
        self.index_dtlb = int(math.log(float(self.num_sets_dtlb), 2))

        # page-table calculations
        self.index_pt = int(math.log(float(self.num_virtual_pg), 2))
        self.offset_pt = int(math.log(float(self.page_size), 2))

    """prints each entry into the config file"""
    def print_config(self):
        # data tlb config
        print("Data TLB contains " + str(self.num_sets_dtlb) + " sets.")
        print("Each set contains " + str(self.set_size_dtlb) + " entries.")
        print("Number of bits used for the index is " + str(self.index_dtlb) + ".\n")

        # page table config
        print("Number of virtual pages is " + str(self.num_virtual_pg) + ".")
        print("Number of physical pages is " + str(self.num_physical_pg) + ".")
        print("Each page contains " + str(self.page_size) + " bytes.")
        print("Number of bits used for the page table index is " + str(self.index_pt) + ".")
        print("Number of bits used for the page offset is " + str(self.offset_pt) + ".\n")

        # data cache config
        print("D-cache contains " + str(self.num_sets_datacache) + " sets.")
        print("Each set contains " + str(self.set_size_datacache) + " entries.")
        print("Each line is " + str(self.line_size_datacache) + " bytes.")
        if self.write_back_datacache:
            print("The cache uses a write-allocate and write-back policy.")
        print("Number of bits used for the index is "+ str(self.index_datacache) + ".")
        print("Number of bits used for the offset is " + str(self.offset_datacache) + ".\n")

        # l2-cache config
        print("L2-cache contains " + str(self.num_sets_l2cache) + " sets.")
        print("Each set contains " + str(self.set_size_l2cache) + " entries.")
        print("Each line is " + str(self.line_size_l2cache) + " bytes.")
        if self.write_back_l2cache:
            print("The cache uses a write-allocate and write-back policy.")

        print("Number of bits used for the index is "+ str(self.index_l2cache) + ".")
        print("Number of bits used for the offset is " + str(self.offset_l2cache) + ".\n")

        # boolean config
        if self.virtual_address:
            print("The addresses read in are virtual addresses.\n")
        else:
            print("The addresses read in are physical addresses.\n")

        if not self.tlb:
            print("TLB is disabled in this configuration.\n")

        if not self.l2_cache:
            print("L2 cache is disabled in this configuration.\n")

    def print_header(self):
        if self.virtual_address:
            print("Virtual  Virt.  Page TLB    TLB TLB  PT   Phys        DC  DC          L2  L2")
        else:
            print("Physical Virt.  Page TLB    TLB TLB  PT   Phys        DC  DC          L2  L2")
        print("Address  Page # Off  Tag    Ind Res. Res. Pg # DC Tag Ind Res. L2 Tag Ind Res.")
        print("-------- ------ ---- ------ --- ---- ---- ---- ------ --- ---- ------ --- ----")

        
class Trace:
    def __init__(self, trace):
        self.data = list()
        """takes all data from trace.dat file and stores it"""
        self.take_trace()
        
    """function to take trace data and create trace data objects"""
    def take_trace(self):
        for line in open(trace):
            value = line.strip().split(":")
            dum = TraceLine(value[0], value[1])
            self.data.append(dum)


"""
    Class for taking in the trace data and running functions on this data
"""
class TraceData:
    def __init__(self, config, data, stats, pt, tlb):
        self.data = data
        self.stats = stats
        """config to know how many bits for each"""
        self.config = config
        """page table for physical conversion"""
        self.pt = pt
        self.tlb = tlb

        self.elem, self.ind, self.boolean, self.bool_evic = self.calculate_all()
        self.dc_tg, self.dc_in, self.l2_tg, self.l2_in = DataCache(self.stats, self.config, self.data).do_cache()

    """function to print all of the values in the given results"""
    def print_all(self):
        for val in self.data:
            if val.accesstype == 'R':
                with open('trace.log', 'a') as f:
                    f.write('read at %08x' %val.virtual_address + '\n\n')
            else:
                with open('trace.log', 'a') as f:
                    f.write('write at %08x' %val.virtual_address + '\n\n')

            self.print_line(stats, val.virtual_address, val.virtual_pg_num, 
                            val.pg_offset, val.tlb_tag, val.tlb_ind, 
                            val.tlb_res, val.pt_res, val.physical_pg_num, 
                            val.dc_tag, val.dc_ind, val.dc_res, val.l2_tag, 
                            val.l2_ind, val.l2_res)
            
        """does all necessary calculations for output"""
        if self.boolean == True and self.bool_evic == 1:
            with open('trace.log', 'a') as f:
                f.write('invalidating DC line with tag ' + str(self.dc_tg[self.ind]) + 
                  ' and index '+ str(self.dc_in[self.ind]) +
                  ' since phys page ' + str(self.elem) + ' is being replaced' + '\n' +
                  'invalidating L2 line with tag ' + str(self.l2_tg[self.ind]) +
                  ' and index ' + str(self.l2_in[self.ind]) +
                  ' since phys page '+ str(self.elem) + ' is being replaced')
    
    """function to calculate different values based on shifts"""
    def calculate_all(self):
        i = 0
        ind = 0
        element = 0
        boolean = True
        bool_evic = True
        ppn_list = []

        for val in self.data: 
            # virtual page
            self.calc_virtual_pg_num(val)
            self.calc_pg_offset(val)

            # tlb 
            self.calc_tlb_tag(val)
            self.calc_tlb_index(val)

            if self.config.tlb:
                # if hit then don't go to pagetable
                val.hexaddress = self.tlb.check_tlb(val)
                
            if self.config.virtual_address:
                #virtual to physical address conversion
                add, bool_evic, ppn = self.pt.convert_to_phy(val)
                val.hexaddress = add
                ppn_list.append(ppn)
                
            self.calc_physical_pg_num(val)
                        
            if self.config.virtual_address:
                ''' Check if given list contains any duplicates '''  
                setOfElems = set()
                for e1 in ppn_list:
                    if e1 in setOfElems:
                        boolean = True
                        ind = ppn_list.index(e1)
                        element = e1
                    else:
                        setOfElems.add(e1)    
                        boolean = False
                        ind = ppn_list.index(e1)
                        element = e1
            i += 1
        
        return element, ind, boolean, bool_evic


    """function for printing all data"""
    def print_line(self, stats, hexaddress, virtual_pg_num, pg_offset, 
                   tlb_tag, tlb_ind, tlb_res, pt_res, physical_pg_num, dc_tag, 
                   dc_ind, dc_res, l2_tag, l2_ind, l2_res):
             
        if tlb_res == "hit ":
            pt_res = ""
        elif self.config.virtual_address:
            pt_res = pt_res
                
        if not self.config.virtual_address and not self.config.tlb and not self.config.l2_cache:
            l2_tag = ""
            l2_ind = ""
            l2_res = ""
            tlb_tag = ""
            tlb_ind = ""
            tlb_res = ""
            pt_res = ""
            virtual_pg_num = ""
            print('%08x' % hexaddress,'%6s' % virtual_pg_num,'%4x' % pg_offset,
                 '%6s %3s %4s' % (tlb_tag, tlb_ind, tlb_res),
                 '%4s' % pt_res,'%4x %6x %3x %4s' % (physical_pg_num, dc_tag, dc_ind, dc_res),
                 '%6s %3s %4s' % (l2_tag, l2_ind, l2_res),)

        if not self.config.virtual_address and not self.config.tlb and self.config.l2_cache:
            tlb_tag = ""
            tlb_ind = ""
            tlb_res = ""
            pt_res = ""
            virtual_pg_num = ""
            print('%08x' % hexaddress,'%6s' % virtual_pg_num,'%4x' % pg_offset,
                 '%6s %3s %4s' % (tlb_tag, tlb_ind, tlb_res),
                 '%4s' % pt_res,'%4x %6x %3x %4s' % (physical_pg_num, dc_tag, dc_ind, dc_res),
                 '%6s %3s %4s' % (l2_tag, l2_ind, l2_res),)

        if self.config.virtual_address and not self.config.tlb and self.config.l2_cache:
            tlb_tag = ""
            tlb_ind = ""
            tlb_res = ""
            pt_res = ""
            print('%08x' % hexaddress,'%6x' % virtual_pg_num,'%4x' % pg_offset,
                 '%6s %3s %4s' % (tlb_tag, tlb_ind, tlb_res),
                 '%4s' % pt_res,'%4x %6x %3x %4s' % (physical_pg_num, dc_tag, dc_ind, dc_res),
                 '%6s %3s %4s' % (l2_tag, l2_ind, l2_res),)
        
        if self.config.virtual_address and self.config.tlb and self.config.l2_cache: 
            print('%08x' % hexaddress,'%6x' % virtual_pg_num,'%4x' % pg_offset,
                 '%6x %3x %4s' % (tlb_tag, tlb_ind, tlb_res),
                 '%4s' % pt_res,'%4x %6x %3x %4s' % (physical_pg_num, dc_tag, dc_ind, dc_res),
                 '%6s %3s %4s' % (l2_tag, l2_ind, l2_res),)
                
    """virtual page number"""  
    def calc_virtual_pg_num(self, val):
        # calculate size of the pg_num
        size = config.offset_pt
        mask = 2 ** 32 - 1
        mask = mask << size
        res = val.hexaddress & mask
        val.virtual_pg_num = res >> size

    """page offset"""
    def calc_pg_offset(self, val):
        offset = config.offset_pt
        mask = 2 ** offset - 1
        val.pg_offset = val.hexaddress & mask

    """tag for tlb"""
    def calc_tlb_tag(self, val):
        shift = config.index_dtlb
        mask = sys.maxsize
        mask = mask << shift
        res = val.virtual_pg_num & mask
        res = res >> shift
        val.tlb_tag = res

    """index for tlb"""
    def calc_tlb_index(self, val):
        mask = 2 ** config.index_dtlb - 1
        res = val.virtual_pg_num & mask
        val.tlb_ind = res
    
    """calculates the physical page number"""
    def calc_physical_pg_num(self, val):
        size = config.offset_pt
        mask = 2 ** 32 - 1
        mask = mask << size
        res = val.hexaddress & mask
        val.physical_pg_num = res >> size

    """offset for data cache"""
    def calc_dc_offset(self, val):
        mask = 2 ** config.d_cache_offset - 1
        res = val.virtual_address & mask
        val.dc_offset = res

        
"""
    class for storing each trace data entry
"""
class TraceLine:
    def __init__(self, accesstype, hexaddress):
        self.accesstype = accesstype
        self.hexaddress = int(hexaddress, 16)

        self.virtual_address = self.hexaddress

        self.virtual_pg_num = ""
        self.pg_offset = ""
        
        self.tlb_tag = ""
        self.tlb_ind = ""
        self.tlb_res = ""

        self.pt_res = ""

        self.physical_pg_num = ""

        self.dc_tag = ""
        self.dc_ind = ""
        self.dc_res = ""

        self.l2_tag = ""
        self.l2_ind = ""
        self.l2_res = ""


class Statistics:

    def __init__(self, config):

        self.config = config
        
        self.dtlb_hits = 0
        self.dtlb_misses = 0

        self.pt_hits = 0
        self.pt_faults = 0

        self.dc_hits = 0
        self.dc_misses = 0

        self.l2_hits = 0
        self.l2_misses = 0

        self.total_reads = 0
        self.total_writes = 0

        self.main_mem_refs = 0
        self.pt_refs = 0
        self.disk_refs = 0

    def print_stats(self):

        print("\nSimulation statistics\n")

        print('dtlb hits        : ' + str(self.dtlb_hits))
        print('dtlb misses      : ' + str(self.dtlb_misses))
        if config.tlb:
            print('dtlb hit ratio   : %6.6f\n' % (float(self.dtlb_hits)/(self.dtlb_hits + self.dtlb_misses)))
        else:
            print('dtlb hit ratio   : N/A\n')

        print('pt hits          : ' + str(self.pt_hits))
        print('pt faults        : ' + str(self.pt_faults))
        if config.virtual_address:
            print('pt hit ratio     : %6.6f\n' % (float(self.pt_hits)/(self.pt_hits+self.pt_faults)))
        else:
            print('pt hit ratio     : N/A\n')

        print('dc hits          : ' + str(self.dc_hits))
        print('dc misses        : ' + str(self.dc_misses))
        print('dc hit ratio     : %6.6f\n' % (float(self.dc_hits)/(self.dc_hits + self.dc_misses)))

        print('L2 hits          : ' + str(self.l2_hits))
        print('L2 misses        : ' + str(self.l2_misses))
        if config.l2_cache:
            print('L2 hit ratio     : %6.6f\n' % (float(self.l2_hits)/(self.l2_hits + self.l2_misses)))
        else:
            print('L2 hit ratio     : N/A\n')

        print('Total reads      : ' + str(self.total_reads))
        print('Total writes     : ' + str(self.total_writes))
        print('Ratio of reads   : %6.6f\n' % (float(self.total_reads)/(self.total_reads + self.total_writes)))

        print('main memory refs : ' + str(self.main_mem_refs))
        print('page table refs  : ' + str(self.pt_refs))
        print('disk refs        : ' + str(self.disk_refs))

  
"""
    class for data cache entries
"""
class DataCacheEntry:
    def __init__(self, v, tag, l2_tag):
        self.v = v
        self.tag = tag
        self.lru = 0
        self.l2_tag = l2_tag
        
    def __str__(self):
        return str(str(self.v) + " " + str(self.tag))


"""
    Data cache for computing tag/ind/hits/misses
"""
class DataCache:
    def __init__(self, stats, config, data):
        self.config = config
        self.data = data
        self.stats = stats
        self.l2 = L2Cache(self.stats, self.config)
        self.assoc = int(config.set_size_datacache)
        self.size = int(config.num_sets_datacache)
        self.entries = []
        self.init_cache()

    def init_cache(self):
        for i in range(self.size):
            dum = list()
            for j in range(self.assoc):
                dum.append(DataCacheEntry(0, -1, -1))
            self.entries.append(dum)

    def print_cache(self):
        for i in range(self.size):
            print(i)
            for j in range(self.assoc):
                print(self.entries[i][j])
            print("")

    def do_cache(self):
        # go through each address and see if in cache
        dc_tg = []
        dc_in = []
        l2_tg = []
        l2_in = []

        for i in self.data:
            # dc
            self.calc_dc_tag(i)
            self.calc_dc_index(i)

            res_dc = self.find_in_cache(i)
            if i.accesstype == "W":
                self.stats.total_writes += 1
            else:
                self.stats.total_reads += 1
            if res_dc:
                i.dc_res = "hit "
            else:
                i.dc_res = "miss"

                # l2 cache
                self.calc_l2_tag(i)
                self.calc_l2_index(i)
                res_l2 = self.l2.find_in_cache(i)
                if res_l2:
                    i.l2_res = "hit "
                    self.stats.l2_hits += 1
                else:
                    i.l2_res = "miss"
                    self.stats.l2_misses += 1
                    self.stats.main_mem_refs += 1
                    
            dc_tg.append(i.dc_tag)
            dc_in.append(i.dc_ind)
            l2_tg.append(i.l2_tag)
            l2_in.append(i.l2_ind)
        return dc_tg, dc_in, l2_tg, l2_in
            
    """tag for dc"""
    def calc_dc_tag(self, val):
        shift = config.offset_datacache + config.index_datacache
        mask = sys.maxsize
        mask = mask << shift
        res = val.hexaddress & mask
        res = res >> shift
        val.dc_tag = res

    """index for dc"""
    def calc_dc_index(self, val):
        shift = config.offset_datacache
        mask = 2 ** config.index_datacache - 1
        mask = mask << shift
        res = val.hexaddress & mask
        res = res >> shift
        val.dc_ind = res

    """tag for l2"""
    def calc_l2_tag(self, val):
        shift = config.offset_l2cache + config.index_l2cache
        mask = sys.maxsize
        mask = mask << shift
        res = val.hexaddress & mask
        res = res >> shift
        val.l2_tag = res

    """index for l2"""
    def calc_l2_index(self, val):
        shift = config.offset_l2cache
        mask = 2 ** config.index_l2cache - 1
        mask = mask << shift
        res = val.hexaddress & mask
        res = res >> shift
        val.l2_ind = res
        
        
    """given an address goes to the index and sees if tag matches"""
    def find_in_cache(self, entry):
        if entry.accesstype =="R":
            cur = entry
            d_set = self.entries[cur.dc_ind]
            for i in d_set:
                if i.v is 1 and cur.dc_tag == i.tag:
                    self.reset_and_inc(d_set, cur.dc_tag)
                    self.stats.dc_hits += 1
                    return True

            self.stats.dc_misses += 1

            replace_index, evicted = self.find_index_replace(d_set)
            save = d_set[replace_index]
            if evicted:
                self.l2.add_evicted(save.l2_tag)

            # found place to replace, get dc_tag and make sure lru is 0 and v is 1
            d_set[replace_index].v = 1
            d_set[replace_index].lru = 0
            d_set[replace_index].tag = cur.dc_tag
            d_set[replace_index].l2_tag = cur.l2_tag
#             if a block was evicted, store this value in the l2 cache
            return False
        
        # WRITE BACK, WRITE ALLOCATE
        elif self.config.write_back_datacache and entry.accesstype =="W":
            cur = entry
            d_set = self.entries[cur.dc_ind]
            for i in d_set:
                if i.v is 1 and cur.dc_tag == i.tag:
                    self.reset_and_inc(d_set, cur.dc_tag)
                    stats.dc_hits += 1
#                     replace_index, evicted = self.find_index_replace(d_set)
#                     d_set[replace_index].tag = cur.dc_tag
                    return True

            stats.dc_misses += 1
            
            replace_index, evicted = self.find_index_replace(d_set)
            save = d_set[replace_index]
            if evicted:
                self.l2.add_evicted(save.l2_tag)

            # found place to replace, must get dc_tag and make sure lru is 0 and v is 1
            d_set[replace_index].v = 1
            d_set[replace_index].lru = 0
            d_set[replace_index].tag = cur.dc_tag
            d_set[replace_index].l2_tag = cur.l2_tag
            return False
        
        # WRITE THROUGH, NO WRITE ALLOCATE
        elif not self.config.write_back_datacache and entry.accesstype =="W":
            cur = entry
            d_set = self.entries[cur.dc_ind]
            for i in d_set:
                if i.v is 1 and cur.dc_tag == i.tag:
                    self.reset_and_inc(d_set, cur.dc_tag)
                    stats.dc_hits += 1
                    replace_index, evicted = self.find_index_replace(d_set)
                    # found place to replace, must get dc_tag and make sure lru is 0 and v is 1
                    d_set[replace_index].v = 1
                    d_set[replace_index].lru = 0
                    d_set[replace_index].tag = cur.dc_tag
                    d_set[replace_index].l2_tag = cur.l2_tag
                    return True

            replace_index, evicted = self.find_index_replace(d_set)
            stats.dc_misses += 1
            # found place to replace, must get dc_tag and make sure lru is 0 and v is 1
            d_set[replace_index].v = 1
            d_set[replace_index].lru = 0
            d_set[replace_index].l2_tag = cur.l2_tag
            return False
        
    """function to increment all lru values and reset the one that was just used"""
    def reset_and_inc(self, d_set, reset):
        for i in d_set:
            if i.v is 1:
                if i.tag is reset:
                    i.lru = 0
                else:
                    i.lru = i.lru + 1


    """function to find index of replaceable value in the set"""
    def find_index_replace(self, d_set):
        ind = 0
        # look for a spot that is not valid
        for i in d_set:
            if i.v is 1:
                i.v = 0
                return ind, False
            ind += 1

        # find greatest LRU value and return the index of it in the d_set
        max_val = d_set[0]
        max_ind = 0
        
        ind = 0
        for i in d_set:
            if i.lru > max_val.lru:
                max_val = i
                max_ind = ind
            ind += 1

        return max_ind, True

    
"""
    L2 Cache entry class
"""
class L2CacheEntry:
    def __init__(self, v, tag):
        self.v = v
        self.tag = tag
        self.lru = 0

    def __str__(self):
        return str(str(self.v) + " " + str(self.tag))

class L2Cache:
    def __init__(self, stats, config):
        self.config = config
        self.stats = stats
        self.assoc = int(config.set_size_l2cache)
        self.size = int(config.num_sets_l2cache)
        self.entries = []
        self.init_cache()

    def init_cache(self):
        for i in range(self.size):
            dum = list()
            for j in range(self.assoc):
                dum.append(L2CacheEntry(0, -1))
            self.entries.append(dum)

    def print_cache(self):
        for i in range(self.size):
            print(i)
            for j in range(self.assoc):
                print(self.entries[i][j])
            print("")

    """given an address goes to the index and sees if tag matches"""
    def find_in_cache(self, entry):    
        if entry.accesstype =="R":
            cur = entry
            d_set = self.entries[cur.l2_ind]
            for i in d_set:
                if i.v is 1 and cur.l2_tag == i.tag:
                    self.reset_and_inc(d_set, cur.l2_tag)
                    return True

            replace_index = self.find_index_replace(d_set)

            d_set[replace_index].v = 1
            d_set[replace_index].lru = 0
            d_set[replace_index].tag = cur.l2_tag
            return False
        
        # WRITE BACK, WRITE ALLOCATE
        elif self.config.write_back_datacache and entry.accesstype =="W":
            cur = entry
            d_set = self.entries[cur.l2_ind]
            for i in d_set:
                if i.v is 1 and cur.l2_tag == i.tag:
                    self.reset_and_inc(d_set, cur.l2_tag)
#                     replace_index = self.find_index_replace(d_set)
#                     d_set[replace_index].tag = cur.l2_tag
                    return True
            
            replace_index = self.find_index_replace(d_set)

            d_set[replace_index].v = 1
            d_set[replace_index].lru = 0
            d_set[replace_index].tag = cur.l2_tag
            return False
        
        # WRITE THROUGH, NO WRITE ALLOCATE
        elif not self.config.write_back_datacache and entry.accesstype =="W":
            cur = entry
            d_set = self.entries[cur.l2_ind]
            for i in d_set:
                if i.v is 1 and cur.l2_tag == i.tag:
                    self.reset_and_inc(d_set, cur.l2_tag)
                    stats.l2_hits += 1
                    replace_index = self.find_index_replace(d_set)
                    d_set[replace_index].v = 1
                    d_set[replace_index].lru = 0
                    d_set[replace_index].tag = cur.l2_tag
                    return True

            replace_index = self.find_index_replace(d_set)
            d_set[replace_index].v = 1
            d_set[replace_index].lru = 0
            return False
    
    """function to increment all lru values and reset the one that was just used"""
    def reset_and_inc(self, d_set, reset):
        for i in d_set:
            if i.v is 1:
                if i.tag is reset:
                    i.lru = 0
                else:
                    i.lru = i.lru + 1


    """function to find index of replaceable value in the set"""
    def find_index_replace(self, d_set):
        ind = 0
        # look for a spot that is not valid
        for i in d_set:
            if i.v is 0:
                i.v = 1
                return ind
            ind += 1

        # find greatest LRU value and return the index of it in the d_set
        max_val = d_set[0]
        max_ind = 0
        
        ind = 0
        for i in d_set:
            if i.lru > max_val.lru:
                max_val = i
                max_ind = ind
            ind += 1

        return max_ind
    
    """function to add the value that is evicted from the data cache"""
    def add_evicted(self, tag):
        replace_ind = self.find_index_replace(self.entries[0])
        self.entries[0][replace_ind].v = 1
        self.entries[0][replace_ind].lru = 0
        self.entries[0][replace_ind].tag = tag


"""
    Physical page table entries class
    done in a round robin fashion
    LRU replacement
"""
class PhysicalPage:
    def __init__(self):
        self.v = 0
        self.lru = 0
        self.init_accesses = 0

        
"""
    Physical page table class
"""
class PhysicalPageTable:
    def __init__(self, config):
        self.config = config
        self.size = self.config.num_physical_pg
        self.pages = list()
        self.init_table()


    def init_table(self):
        for i in range(int(self.size)):
            self.pages.append(PhysicalPage())

    # find a page and return the page number
    def find_page(self):
        replace_page, evicted = self.find_index_replace()
        return replace_page, evicted

    """function to increment all lru values and reset the one that was just used"""
    def inc(self):
        for i in self.pages:
            if i.v is 1:
                i.lru = i.lru + 1


    """function to find index of replaceable value in the set"""
    def find_index_replace(self):
        ind = 0
        # look for a spot that is not valid
        for i in self.pages:
            if i.v is 0:
                i.v = 1
                return ind, False
            ind += 1

        # find greatest LRU value and return the index of it in the d_set
        max_val = self.pages[0]
        max_ind = 0

        ind = 0
        for i in self.pages:
            if i.lru > max_val.lru:
                max_val = i
                max_ind = ind
            ind += 1
            
        return max_ind, True


"""
    virtual page table entry
"""
class PageTableEntry:
    def __init__(self):
        self.phys_page = -1
        self.v = 0

        
"""
    virtual page table implementation
    will take a virtual address and convert it to a physical address
    with a member funciton
"""
class PageTable:
    def __init__(self, stats, config):
        self.stats = stats
        self.config = config
        self.size = int(self.config.num_virtual_pg)
        self.entries = list()
        # physical page table
        self.phys_table = PhysicalPageTable(self.config)
        self.init_table()
        self.invalid = list()

    def init_table(self):
        for i in range(self.size):
            self.entries.append(PageTableEntry())

    # take the virtual address then see if it has a page table value,
    # if it doesn't have a value then go to page table and use find a page
    # to assign to it
    def convert_to_phy(self, add):
        bool_evic = 0
        ppn = 0
        # check if valid entry in vpt
        # store the indexed value
        if add.tlb_res == "miss":
            self.stats.pt_refs += 1
        entry = self.entries[add.virtual_pg_num]
        
        # entry is valid, convert with the physical page instead of the virtual page #
        if entry.v:
            self.phys_table.inc()
            # reset lru for this page number
            self.phys_table.pages[entry.phys_page].lru = 0
            add.pt_res = "hit "
            if add.tlb_res == "miss":
                self.stats.pt_hits += 1
            bool_evic = 0
            add = self.replace_virtual_num(entry.phys_page, add)
            ppn = entry.phys_page
            return add, bool_evic, ppn

        else:
            add.pt_res = "miss"
            entry.phys_page, evicted = self.phys_table.find_page()
            
            # find all virtual pages that have this phys_page and invalidate them
            if evicted:
                self.invalidate_pages(entry.phys_page)
                bool_evic = 1

            entry.v = 1
            self.stats.pt_faults += 1
            self.stats.disk_refs += 1
            add = self.replace_virtual_num(entry.phys_page, add)
            ppn = entry.phys_page
            return add, bool_evic, ppn
        
    """
        takes in page and shifts that and XOR's with the address space pertaining to the num
    """
    def replace_virtual_num(self, page, add):
        shift = config.offset_pt
        offset = add.pg_offset
        new_add = (page << shift) | offset
        return new_add

    """
        takes in phys page number and goes through all pages and invalidates them
    """
    def invalidate_pages(self, page_num):
        inv = 0
        for i in self.entries:
            if i.phys_page == page_num:
                i.v = 0

        
"""
    class for TLBEntry
"""
class TLBEntry:
    def __init__(self):
        self.v = 0
        self.tag = -1
        self.v_page = -1
        self.phys_page = -1

        
"""
    TLB for address conversion
    valid - v
    virtual page number
    physical page number
"""
class TLB:
    def __init__(self, stats, config):
        self.config = config
        self.assoc = int(config.set_size_dtlb)
        self.size = int(config.num_sets_dtlb)
        self.entries = []
        self.init_cache()

    def init_cache(self):
        for i in range(self.size):
            dum = list()
            for j in range(self.assoc):
                dum.append(TLBEntry())
            self.entries.append(dum)

    """given an address goes to the index and sees if tag matches"""
    def check_tlb(self, entry):
        cur = entry
        line = self.entries[cur.tlb_ind]
        for i in line:
            if i.v is 1 and cur.tlb_tag == i.tag:
                # if is valid and tag matches, reset and inc other lru's
                cur.tlb_res = "hit "
                stats.dtlb_hits += 1
                self.reset_and_inc(line, cur.tlb_tag)
                return True

        # if not TLB bring it in and remove other value
        cur.tlb_res = "miss"
        stats.dtlb_misses += 1
        
        replace_index, evicted = self.find_index_replace(line)
        line[replace_index].v = 1
        line[replace_index].lru = 0
        line[replace_index].tag = cur.tlb_tag
        line[replace_index].v_page = cur.virtual_pg_num

        return False

    """function to increment all lru values and reset the one that was just used"""
    def reset_and_inc(self, d_set, reset):
        for i in d_set:
            if i.v is 1:
                if i.tag is reset:
                    i.lru = 0
                else:
                    i.lru = i.lru + 1

    """function to find index of replaceable value in the set"""
    def find_index_replace(self, d_set):
        ind = 0
        # look for a spot that is not valid
        for i in d_set:
            if i.v is 0:
                i.v = 1
                return ind, False
            ind += 1

        # find greatest LRU value and return the index of it in the d_set
        max_val = d_set[0]
        max_ind = 0
        ind = 0
        for i in d_set:
            if i.lru > max_val.lru:
                max_val = i
                max_ind = ind
            ind += 1

        return max_ind, True



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(action='store', dest='config_file', help='The config file name.')
    parser.add_argument(action='store', dest='trace_data', help='The trace data file name.')

    args = parser.parse_args()
    config_file = args.config_file
    trace_data = args.trace_data

    open("trace.log", "w").close()

    config_file = config_file #'trace.config'
    config = Config(config_file)
    trace = trace_data #'trace.dat'
    stats = Statistics(config)
    pagetable = PageTable(stats, config)
    tlb = TLB(stats, config)
    data = Trace(trace)
    out = TraceData(config, data.data, stats, pagetable, tlb)
    out.print_all()
    stats.print_stats()


