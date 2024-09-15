from flask import g, request

from ..classes import ArtworkEntry


def filterEntriesFromPreferences(entries: list[ArtworkEntry]):

    new = entries.copy()

    for entry in entries:
        if request.cookies.get("PyXivHideAI") == "1" and entry.isAI:
            print("FILTER   | Delete", entry, "because isAI =", entry.isAI)
            new.remove(entry)

        if request.cookies.get("PyXivHideR18") == "1" and entry.xRestrict != 0:
            print(
                "FILTER   | Delete",
                entry,
                "due to rating",
                entry.xRestrictClassification,
            )
            try:
                new.remove(entry)
            except ValueError:
                print(
                    "FILTER   | Cannot delete",
                    entry,
                    "it may have already been deleted by AI filter.",
                )

    if new != entries:
        g.omittedByFilter = True

    return new
