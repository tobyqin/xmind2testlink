def xmind_to_dict(file_path):
    """Open and convert xmind to dict type."""
    from .xreader import open_xmind, get_sheets, sheet_to_dict

    open_xmind(file_path)
    data = []

    for s in get_sheets():
        data.append(sheet_to_dict(s))

    return data


def get_default_sheet(d):
    assert len(d) >= 0, 'Invalid xmind: should have at least 1 sheet!'
    return d[0]
