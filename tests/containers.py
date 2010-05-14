import redis
import unittest
from redisco import containers as cont

class SetTestCase(unittest.TestCase):
    def setUp(self):
        self.client = redis.Redis(host='localhost', port=6380, db=10)
        self.client.flushdb()

    def tearDown(self):
        self.client.flushdb()

    def test_common_operations(self):
        fruits = cont.Set(key='fruits', db=self.client)
        fruits.add('apples')
        fruits.add('oranges')
        self.assertEqual(set(['apples', 'oranges']), fruits.all())

        # remove
        fruits.discard('apples')
        self.assertEqual(set(['oranges']), fruits.all())
        self.assertRaises(KeyError, fruits.remove, 'apples')

        # in
        self.assertTrue('oranges' in fruits)
        self.assertTrue('apples' not in fruits)

        # len
        self.assertEqual(1, len(fruits))

        # pop
        self.assertEqual('oranges', fruits.pop())

        # copy
        fruits.add('apples')
        fruits.add('oranges')
        basket = fruits.copy('basket')
        self.assertEqual(set(['apples', 'oranges']), basket.all())

        # update
        o = cont.Set('o', self.client)
        o.add('kiwis')
        fruits.update(o)
        self.assertEqual(set(['kiwis', 'apples', 'oranges']),
                fruits.all())

    def test_comparisons(self):
        all_pls = cont.Set(key='ProgrammingLanguages', db=self.client)
        my_pls = cont.Set(key='MyPLs', db=self.client)
        o_pls = cont.Set(key='OPLs', db=self.client)
        all_pls.add('Python')
        all_pls.add('Ruby')
        all_pls.add('PHP')
        all_pls.add('Lua')
        all_pls.add('Java')
        all_pls.add('Pascal')
        all_pls.add('C')
        all_pls.add('C++')
        all_pls.add('Haskell')
        all_pls.add('C#')
        all_pls.add('Go')

        my_pls.add('Ruby')
        my_pls.add('Python')
        my_pls.add('Lua')
        my_pls.add('Haskell')

        o_pls.add('Ruby')
        o_pls.add('Python')
        o_pls.add('Lua')
        o_pls.add('Haskell')

        # equality
        self.assertNotEqual(my_pls, all_pls)
        self.assertEqual(o_pls, my_pls)

        fruits = cont.Set(key='fruits', db=self.client)
        fruits.add('apples')
        fruits.add('oranges')

        # disjoint
        self.assertTrue(fruits.isdisjoint(o_pls))
        self.assertFalse(all_pls.isdisjoint(o_pls))

        # subset
        self.assertTrue(my_pls < all_pls)
        self.assertTrue(all_pls > my_pls)
        self.assertTrue(o_pls >= my_pls)
        self.assertTrue(o_pls <= my_pls)
        self.assertTrue(my_pls.issubset(all_pls))
        self.assertTrue(my_pls.issubset(o_pls))
        self.assertTrue(o_pls.issubset(my_pls))

        # union
        self.assertEqual(set(['Ruby', 'Python', 'Lua', 'Haskell', 'apples',
            'oranges']), fruits.union(my_pls))
        self.assertEqual(set(['Ruby', 'Python', 'Lua', 'Haskell', 'apples',
            'oranges']), fruits | my_pls)

        # intersection
        self.assertEqual(set([]), fruits.intersection(my_pls))
        self.assertEqual(my_pls.all(), all_pls & my_pls)

        # difference
        self.assertEqual(set(['Ruby', 'Python', 'Lua', 'Haskell']),
                my_pls - fruits)
        self.assertEqual(set(['apples', 'oranges']), fruits - my_pls)

        # symmetric difference
        o_pls.add('C++')
        o_pls.add('C#')
        o_pls.add('Go')
        my_pls.add('Pascal')

        self.assertEqual(set(['C++', 'C#', 'Go', 'Pascal']),
                my_pls.symmetric_difference(o_pls))

    def test_operations_with_updates(self):
        abc = cont.Set('abc', self.client)
        for c in 'abc':
            abc.add(c)

        def_ = cont.Set('def', self.client)
        for c in 'def':
            def_.add(c)

        # __ior__
        abc |= def_
        self.assertEqual(set(['a', 'b', 'c', 'd', 'e', 'f']),
                abc.all())

        abc &= def_
        self.assertEqual(set(['d', 'e', 'f']), abc.all())

        for c in 'abc':
            abc.add(c)
        abc -= def_
        self.assertEqual(set(['a', 'b', 'c']), abc.all())


class ListTestCase(unittest.TestCase):
    def setUp(self):
        self.client = redis.Redis(host='localhost', port=6380, db=10)
        self.client.flushdb()

    def tearDown(self):
        self.client.flushdb()

    def test_common_operations(self):
        alpha = cont.List('alpha', self.client)

        # append
        alpha.append('a')
        alpha.append('b')

        # len
        self.assertEqual(2, len(alpha))

        num = cont.List('num', self.client)
        num.append('1')
        num.append('2')

        # extend and iter
        alpha.extend(num)
        self.assertEqual(['a', 'b', '1', '2'], alpha.all())
        alpha.extend(['3', '4'])
        self.assertEqual(['a', 'b', '1', '2', '3', '4'], alpha.all())

        # contains
        self.assertTrue('b' in alpha)
        self.assertTrue('2' in alpha)
        self.assertTrue('5' not in alpha)

        # shift and unshift
        num.unshift('0')
        self.assertEqual(['0', '1', '2'], num.members)
        self.assertEqual('0', num.shift())
        self.assertEqual(['1', '2'], num.members)

        # push and pop
        num.push('4')
        self.assertEqual('4', num.pop())
        self.assertEqual(['1', '2'], num.members)

        # trim
        alpha.trim(0, 1)
        self.assertEqual(['a', 'b'], alpha.all())

        # remove
        alpha.remove('b')
        self.assertEqual(['a'], alpha.all())

        # setitem
        alpha[0] = 'A'
        self.assertEqual(['A'], alpha.all())


        # iter
        alpha.push('B')
        for e, a in zip(alpha, ['A', 'B']):
            self.assertEqual(a, e)
        self.assertEqual(['A', 'B'], list(alpha))

        # slice
        alpha.extend(['C', 'D', 'E'])
        self.assertEqual(['A', 'B', 'C', 'D', 'E'], alpha[:])
        self.assertEqual(['B', 'C'], alpha[1:2])

        alpha.reverse()
        self.assertEqual(['E', 'D', 'C', 'B', 'A'], list(alpha))