#!/usr/bin/env python3

# Compare two HID descriptors to see if they are equivalent
#
# Two HID descriptors are considered equivalent if they share the
# same set of state tables for each main item.


from hid_read import read_hid_binary_items, parse_item_bytes
from hid_state import get_state_tables

import sys
import copy


def _normalize_state_table(table):
    table = copy.deepcopy(table)
    for key in table.keys():
        del table[key]["used"]
        del table[key]["index"]
    return table


def compare_state_tables(stateA, stateB):
    idxA, itemA, tableA = stateA
    tableA = _normalize_state_table(tableA)
    idxB, itemB, tableB = stateB
    tableB = _normalize_state_table(tableB)

    if itemA != itemB:
        print(itemA)
        print(itemB)
        raise Exception("Items differ at indicies {}/{}".format(idxA, idxB))
    if tableA != tableB:
        print(tableA)
        print(tableB)
        raise Exception("States differ at indicies {}/{}".format(idxA, idxB))


def compare(itemsA, itemsB):
    statesA = get_state_tables(itemsA)
    statesB = get_state_tables(itemsB)
    for stateA, stateB in zip(statesA, statesB):
        compare_state_tables(stateA, stateB)


if __name__ == "__main__":
    itemsA = read_hid_binary_items(sys.argv[1])
    itemsB = read_hid_binary_items(sys.argv[2])
    try:
        compare(itemsA, itemsB)
        print("Descriptors are equivalent")
    except Exception as e:
        print(e)
