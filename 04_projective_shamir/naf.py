def make_naf(dec_val):
    bins = [0] + [ int(x) for x in (bin(dec_val)[2:]) ] # add leading 0, get binary representation of value
    bins.append(0)
    rev_bins = bins[::-1]   # append 0 at the end and reverse
    naf_list = []
    for i in range(0, len(rev_bins) - 1):
        x = rev_bins[i]
        y = rev_bins[i+1]
        if(x == 1 and y == 1):
            naf_list.append(0)
        if(x == 0 and y == 0):
            naf_list.append(0)
        if(x == 1 and y == 0):
            naf_list.append(1)
        if(x == 0 and y == 1):
            naf_list.append(-1)
    return naf_list[::-1]

def extend_naf(binlist, size):
    l = len(binlist)
    while(l < size):
       binlist.insert(0,0)
       l = len(binlist)
    return binlist

def extend_naf_to_even(binlist):
    l = len(binlist)
    while ((l % 2) != 0):
        binlist.insert(0, 0)
        l = len(binlist)
    return binlist


def make_non_zero(dec_val):
    bins = [ int(x) for x in (bin(dec_val)[2:]) ] # get binary representation of value
    rev_bins = bins[::-1]
    if(rev_bins[0] != 1):
        raise ValueError("non-zero ternary representation works only if LSB == 1 (use k + modulo?)")
    for i in range(0, len(rev_bins) - 1):
        x = rev_bins[i]
        y = rev_bins[i+1]
        if(x == 1 and y == 0):
            rev_bins[i+1] = 1
            rev_bins[i] = -1
    return rev_bins[::-1]

def extend_non_zero(binlist, size):
    l = len(binlist)
    while (l < size):
        if(binlist[0] == 1):
            binlist[0] = -1
            binlist.insert(0, 1)
        elif(binlist[0] == -1):
            binlist[0] = 1
            binlist.insert(0, -1)
        else:
            raise ValueError("unknown digit encountered: "+str(binlist[0]))
        l = len(binlist)
    return binlist

def undo_naf(naf_list):
    rev_naf_list = naf_list[::-1]
    dec_val = 0
    for i in range(0, len(naf_list)):
        dec_val += rev_naf_list[i] * (2**i)
    return dec_val


    
#print(make_naf(131))
#print(undo_naf([1,0,0,0,-1]))

#print(make_naf(7))
#for i in range(0,32):
#    print(undo_naf(make_naf(i)))

#print(make_non_zero(23))

#naf1 = extend_non_zero(make_non_zerof(23),256)
#print(naf1)
#print(len(naf1))
#print(undo_naf(naf1))