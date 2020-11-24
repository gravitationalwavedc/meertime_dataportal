def singular_dict(output):
    """convert dict[key][0] to dict[key]"""
    if output is None:
        return None
    output_dict = []
    for k in output.keys():
        output_dict[k] = output[k][0]
    return output_dict
