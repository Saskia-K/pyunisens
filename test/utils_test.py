# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 16:37:07 2020

@author: skjerns
"""
import os
from unisens import utils
import unittest
import shutil
import tempfile
import numpy as np



class Testing(unittest.TestCase):
    
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix='unisens')
        
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    

    def test_read_write_csv(self):        
        file = os.path.join(self.tmpdir, 'file.csv')


        with self.assertRaises(AssertionError):
            utils.write_csv(file, [3,4,4], sep=',', decimal_sep=',')
            
        with self.assertRaises(AssertionError):
            utils.write_csv(file, 'test', sep=',', decimal_sep=',')
            
        one_column = [[x] for x in range(5)]
        utils.write_csv(file, one_column)
        read = utils.read_csv(file)
        self.assertSequenceEqual(one_column, read)
        
        one_column = [x for x in range(5)]
        utils.write_csv(file, one_column, comment='test\ntest')
        read = utils.read_csv(file)
        self.assertSequenceEqual(one_column, [x[0]for x in read])
        
        two_column = [[x, str(x+10)+'xf'] for x in range(5)]
        utils.write_csv(file, two_column)
        read = utils.read_csv(file)
        self.assertSequenceEqual(two_column, read)
        
        two_column = [[x, str(x+10)+'xf'] for x in range(5)]
        utils.write_csv(file, two_column, sep=',')
        read = utils.read_csv(file)
        self.assertNotEqual(two_column, read)
        read = utils.read_csv(file, sep=',')
        self.assertEqual(two_column, read) 
        
        var_column = [[x, str(x+10)+'xf'] for x in range(5)]
        var_column[0] = [1,2,3,4,5]
        utils.write_csv(file, var_column)
        read = utils.read_csv(file)
        self.assertEqual(var_column, read) 
        
        with_comment = [[x, str(x+10)+'xf'] for x in range(5)]
        utils.write_csv(file, with_comment, comment='test')
        read = utils.read_csv(file)
        self.assertEqual(with_comment, read) 
        
        one_row = [[x for x in range(5)]]
        utils.write_csv(file, one_row)
        read = utils.read_csv(file)
        self.assertEqual(one_row, read) 
        read = utils.read_csv(file, convert_nums=False)
        self.assertEqual(read, [[str(x) for x in one_row[0]]]) 
        
        float_2d = [[x+1.4, x+5.2] for x in range(5)]
        utils.write_csv(file, float_2d)
        read = utils.read_csv(file)
        self.assertEqual(float_2d, read) 
        
        float_2d = [[x+1.4, x+5.2] for x in range(5)]
        utils.write_csv(file, float_2d, decimal_sep=',')
        read = utils.read_csv(file, decimal_sep=',')
        self.assertEqual(float_2d, read) 
        
        np_1d = np.random.rand(5)
        utils.write_csv(file, np_1d)
        read = np.array(utils.read_csv(file)).squeeze()
        np.testing.assert_array_equal(np_1d, read) 
        
        np_2d = np.random.rand(1,5)
        utils.write_csv(file, np_2d)
        read = np.array(utils.read_csv(file))
        np.testing.assert_array_equal(np_2d, read) 
        
        with self.assertRaises(ValueError):
            utils.write_csv(file, np.random.rand(3,3,3))
        
    def test_make_key(self):
        s = 'abcde12345'
        r = utils.make_key(s)
        self.assertEqual(s,r)

        s = '12abcde12345'
        r = utils.make_key(s)
        self.assertEqual('x_'+s,r)

        s = '1#$%^&*()[]'
        r = utils.make_key(s)
        self.assertEqual('x_1__________',r)
        
    def test_validkey(self):
        with self.assertRaises(AssertionError):
            utils.validkey(4)
        with self.assertRaises(ValueError):
            utils.validkey('4a')
        self.assertEqual('abc', utils.validkey('abc'))
        self.assertEqual('abC', utils.validkey('abC'))

    def test_strip(self):
        self.assertEqual('abc', utils.strip('abc'))
        self.assertEqual('abc', utils.strip('{https:////}{{{{}}}}abc'))
    
if __name__ == '__main__':
    unittest.main()














