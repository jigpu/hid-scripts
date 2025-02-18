#!/usr/bin/env python3

# Calculate the state table for each main item in a hid descriptor


from hid_read import read_hid_binary_items, parse_item_bytes

import sys
import copy


def _get_item_key(item):
    return (item["type"], item["tag"])


def _get_item_data(item):
    return item["data"]


def _table_key_is_local(key):
    key_type, key_tag = key
    return key_type == 2


def _add_state(state_table, item, idx):
    item_key = _get_item_key(item)
    item_data = _get_item_data(item)
    item_used = False

    if _table_key_is_local(item_key):
        item_used = True

    if item_key in state_table:
        if state_table[item_key]["value"] == item_data:
            return idx  # The new value is unnecessary
        elif state_table[item_key]["used"] == False:
            return state_table[item_key]["index"]  # The previous value is unnecessary

    state_table[item_key] = {"value": item_data, "used": item_used, "index": idx}
    return None


def _mark_global_state(state_table):
    keys = [k for k in state_table.keys() if not _table_key_is_local(k)]
    for k in keys:
        state_table[k]["used"] = True


def _remove_local_state(state_table):
    keys = [k for k in state_table.keys() if _table_key_is_local(k)]
    for k in keys:
        del state_table[k]


def update_state_table(stack, item, idx):
    if len(stack) == 0:
        stack.append({})
    state_table = stack[-1]

    ret = None
    if item["type"] == 0:  # Main item
        _remove_local_state(state_table)
        _mark_global_state(state_table)
    elif item["type"] == 1:  # Global item
        if item["tag"] == 0x0A:  # Push
            dup = copy.deepcopy(state_table)
            stack.append(dup)
        elif item["tag"] == 0x0B:  # Pop
            del stack[-1]
        else:
            ret = _add_state(state_table, item, idx)
    elif item["type"] == 2:  # Local item
        ret = _add_state(state_table, item, idx)
    else:  # Reserved
        raise NotImplementedError("Unknown type {} at {}".format(item["type"], idx))
    return ret


def get_state_tables(items):
    result = []
    stack = []

    for idx, item in enumerate(items):
        parsed_item = parse_item_bytes(item)
        if parsed_item["type"] == 0:  # Main item
            dup = copy.deepcopy(stack[-1])
            result.append((idx, item, dup))
        update_state_table(stack, parsed_item, idx)

    return result


if __name__ == "__main__":
    items = read_hid_binary_items(sys.argv[1])
    tables = get_state_tables(items)
    for idx, item, table in tables:
        hex = " ".join(["{:02x}".format(x) for x in item])
        print("{}: {} {}".format(idx, hex, table))
