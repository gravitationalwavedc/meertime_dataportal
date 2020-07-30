#!/usr/bin/env python

# proposal mapping, a guess at this stage
proposal_dict = {
    "SCI-20180516-MB-01": "MeerTime",
    "SCI-20180516-MB-02": "TPA",
    "SCI-20180516-MB-03": "RelBin",
    "SCI-20180516-MB-04": "GC",
    "SCI-20180516-MB-05": "PTA",
    "SCI-20180516-MB-06": "NGC6440",
    "COM-20180801-SB-01": "Commissioning",
}

proposal_adjust_dict = {
    "SCI-2018-0516-MB-01": "SCI-20180516-MB-01",
    "SCI-2018-0516-MB-02": "SCI-20180516-MB-02",
    "SCI-2018-0516-MB-03": "SCI-20180516-MB-03",
    "SCI-2018-0516-MB-04": "SCI-20180516-MB-04",
    "SCI-2018-0516-MB-05": "SCI-20180516-MB-05",
    "SCI-2018-0516-MB-06": "SCI-20180516-MB-06",
}


def fix_proposal(proposal):
    # this is ugly, will need a way of proper handling this, probably manual adjustement is the only realistic option if not controlled by one person.
    if proposal in proposal_dict.keys():
        return proposal
    else:
        if proposal in proposal_adjust_dict.keys():
            proposal = proposal_adjust_dict[proposal]
            return proposal
        else:
            return proposal
