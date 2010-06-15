import sys
sys.path.insert(0, 'build/lib.linux-i686-2.3/')
import khmer

### build a k-table of length L, and test it.

L = 4

# make a new ktable.
kt = khmer.new_ktable(L)

# check to make sure sizes are what we expect.
assert kt.ksize() == L
assert kt.max_hash() == 4**L - 1
assert kt.n_entries() == 4**L

### make sure forward/reverse hash work minimally.
s = 'ATCG'
assert kt.reverse_hash(kt.forward_hash('ATCG')) == s

### make sure they populate the table completely, too!

alphabet = ('A', 'C', 'G', 'T')
def rN(L, d={}, *args):
    if L == 0:
        d["".join(args)] = 1
        return

    for letter in alphabet:
        rN(L-1, d, letter, *args)

    return d.keys()

# generate all L-mers & make sure they all map differently:
all_lmers = rN(L)

occupy_l = []
for i in all_lmers:
    occupy_l.append(kt.forward_hash(i))

occupy_l.sort()
assert occupy_l == range(0, kt.n_entries())

### check to make sure that fwd --> rev --> fwd works.

for i in range(0, kt.n_entries()):
    assert kt.forward_hash(kt.reverse_hash(i)) == i

### consume a test string, and verify that consume works.
    
s = "ATGAGAGACACAGGGAGAGACCCAATTAGAGAATTGGACC"
kt.consume(s)

kt2 = khmer.new_ktable(L)

kt_dict = {}
for start in range(0, len(s) - L + 1):
    word = s[start:start+L]
    n = kt_dict.get(word, 0)
    kt_dict[word] = n + 1

    kt2.count(word)

for i in range(0, kt.n_entries()):
    n = kt.get(i)                       # test 'consume_str' numbers
    n2 = kt_dict.get(kt.reverse_hash(i), 0) # ...against dictionaries,
    n3 = kt2.get(i)                     # and 'count' count.
    n4 = kt.get(kt.reverse_hash(i))     # test 'get' of kmer
    
    assert n == n2
    assert n == n3
    assert n == n4

for i in range(0, kt.n_entries()):
    kt.set(i, 1)

for i in range(0, kt.n_entries()):
    assert(kt.get(i) == 1)

### intersection and update.

kt = khmer.new_ktable(L)
for i in range(0, 4**L / 4):
    kt.set(i*4, 1)

kt2 = khmer.new_ktable(L)
for i in range(0, 4**L / 5):
    kt2.set(i*5, 1)

kt3 = kt.intersect(kt2)

assert kt3.get(20) == 2
for i in range(0, 4**L):
    if kt3.get(i):
        assert i % 4 == 0
        assert i % 5 == 0

kt.update(kt2)
for i in range(0, 4**L):
    if kt.get(i):
        assert i % 4 == 0 or i % 5 == 0

### test clear()

kt.clear()
for i in range(0, 4**L):
    assert kt.get(i) == 0

### test KmerCount class

km = khmer.KmerCount(4)
km.consume('AAAAAC')
expected = (('AAAA', 2), ('AAAC', 1))

for i, (kmer, count) in enumerate(km.pairs):
    e = expected[i]
    assert kmer == e[0], (kmer, i)
    assert count == e[1], (count, i)

assert km['AAAA'] == 2
assert km['AAAC'] == 1

km = khmer.KmerCount(4, report_zero=True)
km.consume('AAAAAC')
expected = (('AAAA', 2), ('AAAC', 1))

i = 0
for kmer, count in km.pairs:
    if count:
        e = expected[i]
        assert kmer == e[0], (kmer, i)
        assert count == e[1], (count, i)
        i += 1

assert i == 2

### test capital letters vs lowercase

km = khmer.KmerCount(4, report_zero=True)
km.consume('AAAAAC'.lower())
expected = (('AAAA', 2), ('AAAC', 1))

assert km['AAAA'] == 2
assert km['AAAC'] == 1

### hooray, done!

print 'SUCCESS, all tests passed.'