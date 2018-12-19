# Copyright 2018 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import unittest

import sensor_msgs.msg

from src.image_geometry import PinholeCameraModel, StereoCameraModel


class TestDirected(unittest.TestCase):

    def setUp(self):
        pass

    def test_monocular(self):
        ci = sensor_msgs.msg.CameraInfo()
        ci.width = 640
        ci.height = 480
        print(ci)
        cam = PinholeCameraModel()
        cam.fromCameraInfo(ci)
        print(cam.rectifyPoint((0, 0)))

        print(cam.project3dToPixel((0, 0, 0)))

    def test_stereo(self):
        lmsg = sensor_msgs.msg.CameraInfo()
        rmsg = sensor_msgs.msg.CameraInfo()
        for m in (lmsg, rmsg):
            m.width = 640
            m.height = 480

        # These parameters taken from a real camera calibration
        lmsg.d = [-0.363528858080088, 0.16117037733986861, -8.1109585007538829e-05,
                  -0.00044776712298447841, 0.0]
        lmsg.k = [430.15433020105519, 0.0, 311.71339830549732, 0.0, 430.60920415473657,
                  221.06824942698509, 0.0, 0.0, 1.0]
        lmsg.r = [0.99806560714807102, 0.0068562422224214027, 0.061790256276695904,
                  -0.0067522959054715113, 0.99997541519165112, -0.0018909025066874664,
                  -0.061801701660692349, 0.0014700186639396652, 0.99808736527268516]
        lmsg.p = [295.53402059708782, 0.0, 285.55760765075684, 0.0, 0.0, 295.53402059708782,
                  223.29617881774902, 0.0, 0.0, 0.0, 1.0, 0.0]

        rmsg.d = [-0.3560641041112021, 0.15647260261553159, -0.00016442960757099968,
                  -0.00093175810713916221]
        rmsg.k = [428.38163131344191, 0.0, 327.95553847249192, 0.0, 428.85728580588329,
                  217.54828640915309, 0.0, 0.0, 1.0]
        rmsg.r = [0.9982082576219119, 0.0067433328293516528, 0.059454199832973849,
                  -0.0068433268864187356, 0.99997549128605434, 0.0014784127772287513,
                  -0.059442773257581252, -0.0018826283666309878, 0.99822993965212292]
        rmsg.p = [295.53402059708782, 0.0, 285.55760765075684, -26.507895206214123, 0.0,
                  295.53402059708782, 223.29617881774902, 0.0, 0.0, 0.0, 1.0, 0.0]

        cam = StereoCameraModel()
        cam.fromCameraInfo(lmsg, rmsg)

        for x in (16, 320, m.width - 16):
            for y in (16, 240, m.height - 16):
                for d in range(1, 10):
                    pt3d = cam.projectPixelTo3d((x, y), d)
                    ((lx, ly), (rx, ry)) = cam.project3dToPixel(pt3d)
                    self.assertAlmostEqual(y, ly, 3)
                    self.assertAlmostEqual(y, ry, 3)
                    self.assertAlmostEqual(x, lx, 3)
                    self.assertAlmostEqual(x, rx + d, 3)

        u = 100.0
        v = 200.0
        du = 17.0
        dv = 23.0
        Z = 2.0
        xyz0 = cam.left.projectPixelTo3dRay((u, v))
        xyz0 = (xyz0[0] * (Z / xyz0[2]), xyz0[1] * (Z / xyz0[2]), Z)
        xyz1 = cam.left.projectPixelTo3dRay((u + du, v + dv))
        xyz1 = (xyz1[0] * (Z / xyz1[2]), xyz1[1] * (Z / xyz1[2]), Z)
        self.assertAlmostEqual(cam.left.getDeltaU(xyz1[0] - xyz0[0], Z), du, 3)
        self.assertAlmostEqual(cam.left.getDeltaV(xyz1[1] - xyz0[1], Z), dv, 3)
        self.assertAlmostEqual(cam.left.getDeltaX(du, Z), xyz1[0] - xyz0[0], 3)
        self.assertAlmostEqual(cam.left.getDeltaY(dv, Z), xyz1[1] - xyz0[1], 3)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestDirected('test_stereo'))
    unittest.TextTestRunner(verbosity=2).run(suite)
