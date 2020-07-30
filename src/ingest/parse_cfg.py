#!/usr/bin/env python


def parse_cfg(cfg_file, tags=None):
    """Written by W. Farah, with a slight tweak by S. Oslowski"""
    """Function that returns config file with given tags as dictionary

    Parameters
    ----------
    cfg_file : str
        full directory to config file
    tags : list
        list of tags to search the cgf_file

    Returns
    -------
    config_dict : dict
        dictionary with keys given in tags, and values
        extracted from cfg_file. If one tag doesn't exist,
        value corresponded will be None, else value is of
        type str, or list if multiple values exist for
        same key.
    """
    if tags is None:
        tags = []
        with open(cfg_file) as o:
            for line in o:
                if line[0] in ["\n", "#"]:
                    continue
                tags.append(line.split()[0])
    config_dict = {}
    with open(cfg_file) as o:
        for line in o:
            if line[0] in ["\n", "#"]:
                continue
            for tag in tags:
                if tag in line:
                    i = line.split()
                    if tag != i[0]:
                        continue
                    config_dict[tag] = []
                    for ii in i[1:]:
                        if "#" in ii:
                            break
                        config_dict[tag].append(ii)
                    if len(config_dict[tag]) == 1:
                        config_dict[tag] = config_dict[tag][0]
                    tags.remove(tag)
    for tag in tags:
        # logging.warning("Couldn't parse <"+tag+"> from "+cfg_file)
        config_dict[tag] = None
    return config_dict
