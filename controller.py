# -*- coding: utf-8 -*-

# python imports
from math import degrees
import numpy as np
# pyfuzzy imports
from fuzzy.storage.fcl.Reader import Reader


class FuzzyController:

    def __init__(self, fcl_path):
        self.system = Reader().load_from_file(fcl_path)

    def _make_input(self, world):
        return dict(
            cp=world.x,
            cv=world.v,
            pa=degrees(world.theta),
            pv=degrees(world.omega)
        )

    def _make_output(self):
        return dict(
            force=0.
        )

    def pa_fuzzy(self, pa):
        y_up_more_right = 0
        y_up_right = 0
        y_up = 0
        y_up_left = 0
        y_up_more_left = 0
        y_down_more_left = 0
        y_down_left = 0
        y_down = 0
        y_down_right = 0
        y_down_more_right = 0
        if pa < 0:
            pa += 360
        if 0 <= pa <= 30:
            y_up_more_right = pa * 1 / 30
        if 30 <= pa <= 60:
            y_up_more_right = pa * -1 * 1 / 30 + 2
            y_up_right = pa * 1 / 30 - 1
        if 60 <= pa <= 90:
            y_up_right = pa * -1 * 1 / 30 + 3
            y_up = pa * 1 / 30 - 2
        if 90 <= pa <= 120:
            y_up = pa * -1 * 1 / 30 + 4
            y_up_left = pa * 1 / 30 - 3
        if 120 <= pa <= 150:
            y_up_left = pa * -1 * 1 / 30 + 5
            y_up_more_left = pa * 1 / 30 - 4
        if 150 <= pa <= 180:
            y_up_more_left = pa * -1 * 1 / 30 + 6
        if 180 <= pa <= 210:
            y_down_more_left = pa * 1 / 30 - 6
        if 210 <= pa <= 240:
            y_down_more_left = pa * -1 * 1 / 30 + 8
            y_down_left = pa * 1 / 30 - 7
        if 240 <= pa <= 270:
            y_down_left = pa * -1 * 1 / 30 + 9
            y_down = pa * 1 / 30 - 8
        if 270 <= pa <= 300:
            y_down = pa * -1 * 1 / 30 + 10
            y_down_right = pa * 1 / 30 - 9
        if 300 <= pa <= 330:
            y_down_right = pa * -1 * 1 / 30 + 11
            y_down_more_right = pa * 1 / 30 - 10
        if 330 <= pa <= 360:
            y_down_more_right = pa * -1 * 1 / 30 + 12
        return dict(
            y_up_more_right=y_up_more_right,
            y_up_right=y_up_right,
            y_up=y_up,
            y_up_left=y_up_left,
            y_up_more_left=y_up_more_left,
            y_down_more_left=y_down_more_left,
            y_down_left=y_down_left,
            y_down=y_down,
            y_down_right=y_down_right,
            y_down_more_right=y_down_more_right
        )

    def pv_fuzzy(self, pv):
        cw_fast = 0
        cw_slow = 0
        stop = 0
        ccw_slow = 0
        ccw_fast = 0
        if pv < -200:
            cw_fast = 1
        if pv > 200:
            ccw_fast = 1
        if -200 <= pv <= -100:
            cw_fast = -0.01 * pv - 1
            cw_slow = 0.01 * pv + 2
        if -100 <= pv <= 0:
            cw_slow = -0.01 * pv
            stop = 0.01 * pv + 1
        if 0 <= pv <= 100:
            stop = -0.01 * pv + 1
            ccw_slow = 0.01 * pv
        if 100 <= pv <= 200:
            ccw_slow = -0.01 * pv + 2
            ccw_fast = 0.01 * pv - 1
        return dict(
            cw_fast=cw_fast,
            cw_slow=cw_slow,
            stop=stop,
            ccw_slow=ccw_slow,
            ccw_fast=ccw_fast
        )

    def rules(self, input_pa, input_pv):
        force_stop = []
        force_left_fast = []
        force_left_slow = []
        force_right_fast = []
        force_right_slow = []
        y_up_more_right = input_pa.get('y_up_more_right')
        y_up_right = input_pa.get('y_up_right')
        y_up = input_pa.get('y_up')
        y_up_left = input_pa.get('y_up_left')
        y_up_more_left = input_pa.get('y_up_more_left')
        y_down_more_left = input_pa.get('y_down_more_left')
        y_down_left = input_pa.get('y_down_left')
        y_down = input_pa.get('y_down')
        y_down_right = input_pa.get('y_down_right')
        y_down_more_right = input_pa.get('y_down_more_right')
        cw_fast = input_pv.get('cw_fast')
        cw_slow = input_pv.get('cw_slow')
        stop = input_pv.get('stop')
        ccw_slow = input_pv.get('ccw_slow')
        ccw_fast = input_pv.get('ccw_fast')

        #  rules
        force_stop.append(max(min(y_up, stop), min(y_up_right, ccw_slow), min(y_up_left, cw_slow)))
        force_right_fast.append(min(y_up_more_right, ccw_slow))
        force_right_fast.append(min(y_up_more_right, cw_slow))
        force_left_fast.append(min(y_up_more_left, ccw_slow))
        force_left_fast.append(min(y_up_more_left, cw_slow))
        force_left_slow.append(min(y_up_more_right, ccw_fast))
        force_right_fast.append(min(y_up_more_right, cw_fast))
        force_right_slow.append(min(y_up_more_left, cw_fast))
        force_left_fast.append(min(y_up_more_left, ccw_fast))
        force_right_fast.append(min(y_down_more_right, ccw_slow))
        force_stop.append(min(y_down_more_right, cw_slow))
        force_left_fast.append(min(y_down_more_left, cw_slow))
        force_stop.append(min(y_down_more_left, ccw_slow))
        force_stop.append(min(y_down_more_right, ccw_fast))
        force_stop.append(min(y_down_more_right, cw_fast))
        force_stop.append(min(y_down_more_left, cw_fast))
        force_stop.append(min(y_down_more_left, ccw_fast))
        force_right_fast.append(min(y_down_right, ccw_slow))
        force_right_fast.append(min(y_down_right, cw_slow))
        force_left_fast.append(min(y_down_left, cw_slow))
        force_left_fast.append(min(y_down_left, ccw_slow))
        force_stop.append(min(y_down_right, ccw_fast))
        force_right_slow.append(min(y_down_right, cw_fast))
        force_stop.append(min(y_down_left, cw_fast))
        force_left_slow.append(min(y_down_left, ccw_fast))
        force_right_slow.append(min(y_up_right, ccw_slow))
        force_right_fast.append(min(y_up_right, stop))
        force_left_slow.append(min(y_up_left, cw_slow))
        force_left_fast.append(min(y_up_left, ccw_slow))
        force_left_fast.append(min(y_up_left, stop))
        force_left_fast.append(min(y_up_right, ccw_fast))
        force_right_fast.append(min(y_up_right, cw_fast))
        force_right_fast.append(min(y_up_left, cw_fast))
        force_left_fast.append(min(y_up_left, ccw_fast))
        force_right_fast.append(min(y_down, stop))
        force_stop.append(min(y_down, cw_fast))
        force_stop.append(min(y_down, ccw_fast))
        force_left_slow.append(min(y_up, ccw_slow))
        force_left_fast.append(min(y_up, ccw_fast))
        force_right_slow.append(min(y_up, cw_slow))
        force_right_fast.append(min(y_up, cw_fast))
        force_stop.append(min(y_up, stop))

        force_stop_max = max(force_stop)
        force_left_fast_max = max(force_left_fast)
        force_left_slow_max = max(force_left_slow)
        force_right_fast_max = max(force_right_fast)
        force_right_slow_max = max(force_right_slow)

        return dict(
            force_stop=force_stop_max,
            force_left_fast=force_left_fast_max,
            force_left_slow=force_left_slow_max,
            force_right_fast=force_right_fast_max,
            force_right_slow=force_right_slow_max
        )

    def defuzzify_force(self, force):
        left_fast = force.get('force_left_fast')
        left_slow = force.get('force_left_slow')
        stop = force.get('force_stop')
        right_slow = force.get('force_right_slow')
        right_fast = force.get('force_right_fast')

        x_left_fast_1 = (left_fast - 5) * 20  # always correct
        x_left_fast_2 = (left_fast + 3) * -20
        x_left_slow_1 = (left_slow - 4) * 20
        x_left_slow_2 = left_slow * -60
        x_stop_1 = (stop - 1) * 60
        x_stop_2 = (stop - 1) * -60
        x_right_slow_1 = right_slow * 60
        x_right_slow_2 = (right_slow - 4) * -20
        x_right_fast_1 = (right_fast + 3) * 20
        x_right_fast_2 = (right_fast - 5) * -20

        x_list = np.linspace(-100, 100, 10000)
        sum_nominator = 0
        sum_denominator = 0

        for x in x_list:
            y = 0
            if -100 <= x < -80:  # first triangle without eshterak
                if x < x_left_fast_1:
                    y = 0.05 * x + 5
                elif x_left_fast_1 < x:
                    y = left_fast

            elif -80 <= x < -60:
                y1 = y2 = 0
                if x_left_fast_1 < x < x_left_fast_2:
                    y1 = left_fast
                elif x_left_fast_2 < x:
                    y1 = -0.05 * x - 3
                if x < x_left_slow_1:
                    y2 = 0.05 * x + 4
                elif x_left_slow_1 < x:
                    y2 = left_slow
                y = max(y1, y2)

            elif -60 <= x < 0:
                y1 = y2 = 0
                if x_left_slow_1 < x < x_left_slow_2:
                    y1 = left_slow
                elif x_left_slow_2 < x:
                    y1 = -(1.0/60) * x
                if x < x_stop_1:
                    y2 = (1.0/60) * x + 1
                elif x_stop_1 < x:
                    y2 = stop
                y = max(y1, y2)

            elif 0 <= x < 60:
                y1 = y2 = 0
                if x_stop_1 < x < x_stop_2:
                    y1 = stop
                elif x_stop_2 < x:
                    y1 = -(1.0 / 60) * x + 1
                if x < x_right_slow_1:
                    y2 = (1.0 / 60) * x
                elif x_right_slow_1 < x:
                    y2 = right_slow
                y = max(y1, y2)

            elif 60 <= x < 80:
                y1 = y2 = 0
                if x_right_slow_1 < x < x_right_slow_2:
                    y1 = right_slow
                elif x_right_slow_2 < x:
                    y1 = -0.05 * x + 4
                if x < x_right_fast_1:
                    y2 = 0.05 * x - 3
                elif x_right_fast_1 < x:
                    y2 = right_fast
                y = max(y1, y2)

            elif 80 <= x <= 100:
                if x < x_right_fast_2:
                    y = right_fast
                elif x_right_fast_2 < x:
                    y = -0.05 * x + 5

            sum_denominator += y
            sum_nominator += x * y
        if sum_denominator == 0:
            return 0
        return sum_nominator / sum_denominator




    def decide(self, world):
        input = self._make_input(world)
        input_pa = self.pa_fuzzy(input.get('pa'))
        input_pv = self.pv_fuzzy(input.get('pv'))
        force = self.rules(input_pa, input_pv)
        defuzzified_force = self.defuzzify_force(force)
        # output = self._make_output()
        # self.system.calculate(self._make_input(world), output)
        return defuzzified_force
