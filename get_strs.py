import itertools
import random
import sys
import operator

random.seed(1475260362)

t = list(range(256))
random.shuffle(t)


def pearson_hash(s):
    h = 0
    for c in s.encode('utf-8'):
        index = h ^ c
        h = t[index]
    return h


def get_shortest_strs_for_hash(username, channel, hash_func, hash_count):

    def get_hash(i):
        return hash_func(str((':' + i, username, channel, i))) % hash_count

    # alphabet_iter = ''.join(str(i) for i in range(10))
    alphabet_iter = ''.join(chr(ord('a') + i) for i in range(26))

    need_hashes = list(range(hash_count))

    found_vars = []

    for length in itertools.count(1):
        vars_ = (''.join(i) for i in
                 itertools.product(alphabet_iter, repeat=length))
        vars_with_hash = sorted((get_hash(i), i) for i in vars_)
        hashes_with_first_var = ((i, next(j)[1]) for i, j in
                                 itertools.groupby(vars_with_hash,
                                                   key=operator.itemgetter(0)))

        for hash_, var in hashes_with_first_var:
            try:
                need_hashes.remove(hash_)
            except ValueError:
                pass
            else:
                found_vars.append((hash_, var))

            if len(need_hashes) == 0:
                return [var for _, var in sorted(found_vars)]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('args: username channel')
    else:
        username = sys.argv[1]
        channel = sys.argv[2]
        print(', '.join(get_shortest_strs_for_hash(username, channel,
                                                   pearson_hash, 8)))
