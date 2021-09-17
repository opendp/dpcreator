from django.test import TestCase

from unittest import skip

# Create your tests here.
from opendp.trans import make_split_dataframe

#from opendp_apps.analysis.tools.dp_mean import dp_mean
from django.test import TestCase


class TestDPMean(TestCase):
    @skip
    def test_dp_mean(self):
        data = '59,1,9,1,0,1\n31,0,1,3,17000,0\n36,1,11,1,0,1\n54,1,11,1,9100,1\n39,0,5,3,37000,0\n34,0,9,1,0,1\n' \
               '93,1,8,1,6000,1\n69,0,13,1,350000,1\n40,1,11,3,33000,1\n27,1,11,1,25000,0\n59,1,13,1,49000,1\n' \
               '31,1,11,3,0,1\n73,1,13,4,35500,0\n89,1,9,1,4000,1\n39,1,10,3,15000,0\n51,1,13,4,120000,1\n' \
               '32,0,9,1,13000,0\n52,0,11,2,45000,0\n24,0,7,1,0,0\n48,1,10,1,4300,1\n51,0,1,3,16000,1\n' \
               '43,1,14,1,365000,1\n29,0,4,3,20000,0\n44,1,15,1,17900,1\n87,1,8,1,3600,0\n27,1,11,3,10800,0\n' \
               '58,0,13,1,60900,1\n32,1,11,3,25000,1\n'

        col_names = ["A", "B", "C", "D", "E"]
        index = "E"
        fixed_value = 0.
        lower = 0.
        upper = 10000.
        n = 1000
        epsilon = 1.
        preprocessor = make_split_dataframe(separator=",", col_names=col_names)
        res = preprocessor >> dp_mean(index, lower, upper, n, fixed_value, epsilon=epsilon)
        dp_mean_value = res(data)
        self.assertEqual(type(dp_mean_value), float)