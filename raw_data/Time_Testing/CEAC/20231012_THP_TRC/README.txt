Time testing of THP sensor that has updated timing code.

The NTP setup for the datalogger was wrong, therefore there are dates that are in the year 2026. The times are invalid and all of those records should be ignored.
Sample from console output:
DS3231 time: (2023, 16, 8, 10, 28, 57, 6, 0)
local time: 2067-03-06 10:28:57

Updated code for the timing did not work as evident from the ends of the log on 10/12/2023.

A future software patch needs applied before good readings will be available.
