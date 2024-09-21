def flatten_json(o):
    o_list = []
    for key in o:
        o_list.append(o[key])
    return o_list