"""Silences all logcat messages until we see no new type of activity for
a certain amount of time. Then communicates to the user that they can
now interact with the device without being interrupted by unrelated logcat
messages.

I wrote this because reading logs is a pain when you're trying to interact
with the device and the logs are constantly being updated by unrelated
activities.

This script is meant to be run with adb logcat piped into it. For example:

$ adb logcat | python logcat_silencer.py
"""

import sys
import time

# The time in seconds that we wait for no new activity before we allow
# the user to interact with the device.
last_new_activity = time.time()

# The set of activities that we have seen so far. We ignore all activities
# that we have seen before until we have not seen any new activity for
# a certain amount of time, so that we can communicate to the user that
# they can now interact with the device.
ignored_activities = set()

# Are we still waiting for no new activity?
still_waiting = True

for line in sys.stdin:

    # extract the activity from the logcat line
    try:
        activity = line.split()[5]
    except IndexError:
        if not line.startswith("--------- beginning of "):
            sys.stderr.write("\rCould not parse line: %s" % line)
        continue

    if activity not in ignored_activities:
        # we've seen a new activity, so we need to either reset the timer...
        if still_waiting:
            ignored_activities.add(activity)
            last_new_activity = time.time()
        # ...or print the line, because we're no longer waiting
        else:
            sys.stdout.write(line)

    if still_waiting:
        # print the time since the last new activity, so that
        # the user knows how long they have to wait before they
        # can interact with the device
        time_since_last_activity = int(time.time() - last_new_activity)
        sys.stderr.write(
            "\r%d / %d   "
            % (time_since_last_activity, len(ignored_activities))
        )
        if time_since_last_activity > 60:
            # print a message to the user that they can now interact with
            # the device
            print("          ")
            sys.stdout.write(
                "No new activity for %d seconds. "
                "You can now interact with the device.\n"
                % time_since_last_activity
            )
            still_waiting = False
