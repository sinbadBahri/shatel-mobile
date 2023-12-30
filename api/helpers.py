def is_title_special(title):
    return title.startswith("$")


def is_valid_description(description):
    return len(description) >= 20
