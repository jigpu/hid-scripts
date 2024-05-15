#!/usr/bin/env python3

# Read through a binary HID descriptor and determine which items are
# important. Specifically highlights global items that:
#
#    - Are replaced before they are used
#    - Set a value already in use
#
# Items like this are bloat and can be removed from a descriptor.
#
# When called with a filename, prints out a list of HID items, one per
# line along with 'True' for important items that must be kept and 'False'
# for items that may be safely removed.

from hid_read import read_hid_binary_items, parse_item_bytes
from hid_state import update_state_table

import sys
import copy


def list_item_importance(items):
    result = [True] * len(items)  # Assume everything is important
    stack = []

    for idx, item in enumerate(items):
        parsed_item = parse_item_bytes(item)
        ret = update_state_table(stack, parsed_item, idx)
        if ret is not None:
            result[ret] = False

    return result


if __name__ == "__main__":
    items = read_hid_binary_items(sys.argv[1])
    importance = list_item_importance(items)
    for idx, element in enumerate(zip(items, importance)):
        hex = " ".join(["{:02x}".format(x) for x in element[0]])
        importance = element[1]
        print("{}: {} {}".format(idx, hex, importance))
