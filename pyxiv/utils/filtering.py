from flask import g, request, current_app

from ..classes import ArtworkEntry


def filterEntriesFromPreferences(entries: list[ArtworkEntry]):

    new = entries.copy()

    for entry in entries:
        if request.cookies.get("PyXivHideAI") == "1" and entry.isAI:
            new.remove(entry)
            continue

        if request.cookies.get("VixipyHideSensitive") == "1" and entry.isSensitive:
            new.remove(entry)
            continue

        if current_app.config["nor18"] and entry.xRestrict >= 1:
            new.remove(entry)
            continue

        if request.cookies.get("PyXivHideR18") == "1" and entry.xRestrict == 1:
            new.remove(entry)
            continue

        if request.cookies.get("PyXivHideR18G") == "1" and entry.xRestrict == 2:
            new.remove(entry)
            continue

        if current_app.debug:
            print("FILTER   |", entry, "OK")

    if current_app.debug:
        print(
            "FILTER   | Results:",
            len(entries),
            "previous,",
            len(entries) - len(new),
            "filtered,",
            len(new),
            "current",
        )

    if new != entries:
        g.omittedByFilter = True

    return new
