This module emulates two-joint manipulator work on the task of picking and placing items with
given positions.

manipulator.py contains "Manipulator" class which emulates manipulator work and gives methods to
               move manipulator arms, hold and release items (grasping is not emulated).
picker.py      contains "Picker" class which emulates manipulator operation logic for collecting
               items with given positions and sizes and putting them to the given places.
demo.py        runs "collecting items" demonstration. It also enables recording video (not by
               default, run demo.collect_items(record_video=True) to record video).

Demo video of algorithm work can be found here: https://drive.google.com/open?id=1Y3JrXx1ToRk-oHNGo4VmklgzQGH4JtsL