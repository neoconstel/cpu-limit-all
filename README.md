# cpulimit all
This simple script (for linux) uses cpulimit to limit all processes to the specified limit.


# execution
simply run in terminal using python
> e.g python3 cpu_limit_all.py

You can even set it as a default startup program as I did, so it runs in the background once you turn on your PC


# settings
- limit: general cpulimit value for all processes
- interval: interval in seconds for which the program should repeatedly check for processes/updated settings
- exempted_programs: the executable name of programs which should not be limited at all.
> (e.g __"wesnoth-1.14"__ will exempt every process ending in "/wesnoth-1.14" or just bearing the name "wesnoth-1.14")

- targeted_limits: executable name of programs which should use a targeted limit instead of the general limit
> (e.g __"vlc": 5__ will limit vlc to 5% cpu irrespective of the value of the general limit)
 
