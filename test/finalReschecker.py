import json
import re
from pathlib import Path


def print_lkh_comparison_by_size(json_paths):
    if isinstance(json_paths, (str, Path)):
        json_paths = [json_paths]

    best_by_size = {}
    worst_by_size = {}
    failed_by_size = {}
    excluded_by_cutoff_by_size = {}

    for json_path in json_paths:
        json_path = Path(json_path)

        size = extract_size_from_filename(json_path.name)

        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        valid_entries = []
        failed_attempts = []
        cutoff_attempts = []

        for name, result in data.items():
            # Skip summary entries
            if not isinstance(result, dict):
                continue

            lkh_result = result.get("LKH")

            # Skip entries without LKH result
            if not isinstance(lkh_result, dict):
                continue

            ai_distance = lkh_result.get("ai_distance")
            lkh_distance = lkh_result.get("other_distance")

            # Collect cutoff cases separately and exclude them from best/worst
            if lkh_result.get("excluded_by_cutoff", False):
                cutoff_attempts.append({
                    "name": name,
                    "ai_distance": ai_distance,
                    "lkh_distance": lkh_distance,
                    "difference": (
                        ai_distance - lkh_distance
                        if isinstance(ai_distance, (int, float))
                        and isinstance(lkh_distance, (int, float))
                        else None
                    )
                })
                continue

            # Detect failed AI attempts
            if (
                lkh_result.get("excluded_by_failed", False)
                or not isinstance(ai_distance, (int, float))
                or ai_distance is None
            ):
                failed_attempts.append(name)
                continue

            difference = ai_distance - lkh_distance
            absolute_difference = abs(difference)

            entry = {
                "json_file": json_path.name,
                "size": size,
                "name": name,
                "ai_distance": ai_distance,
                "lkh_distance": lkh_distance,
                "difference": difference,
                "absolute_difference": absolute_difference,
            }

            valid_entries.append(entry)

        if valid_entries:
            best_by_size[size] = min(
                valid_entries,
                key=lambda entry: entry["absolute_difference"]
            )

            worst_by_size[size] = max(
                valid_entries,
                key=lambda entry: entry["absolute_difference"]
            )

        failed_by_size[size] = sorted(set(failed_attempts))
        excluded_by_cutoff_by_size[size] = cutoff_attempts

    print("\nExcluded by cutoff per size")
    print("---------------------------")
    for size in sorted(excluded_by_cutoff_by_size):
        cutoff_attempts = excluded_by_cutoff_by_size[size]

        print(f"\nSize {size}:")
        if cutoff_attempts:
            for entry in cutoff_attempts:
                print_cutoff_entry(size, entry)
        else:
            print("None")

    print("\nBest AI result per size compared to LKH")
    print("--------------------------------------")
    for size in sorted(best_by_size):
        print_entry(best_by_size[size])

    print("\nWorst AI result per size compared to LKH")
    print("---------------------------------------")
    for size in sorted(worst_by_size):
        print_entry(worst_by_size[size])

    print("\nFailed attempts per size")
    print("------------------------")
    for size in sorted(failed_by_size):
        failed = failed_by_size[size]

        print(f"\nSize {size}:")
        if failed:
            for name in failed:
                print(name)
        else:
            print("None")


def extract_size_from_filename(filename):
    match = re.search(r"results(\d+)\.json", filename)

    if match:
        return int(match.group(1))

    raise ValueError(f"Could not extract size from filename: {filename}")


def print_entry(entry):
    print(
        f"Size {entry['size']:>3} | "
        f"{entry['name']} | "
        f"AI: {entry['ai_distance']} | "
        f"LKH: {entry['lkh_distance']} | "
        f"diff: {entry['difference']} | "
        f"abs diff: {entry['absolute_difference']}"
    )


def print_cutoff_entry(size, entry):
    print(
        f"Size {size:>3} | "
        f"{entry['name']} | "
        f"AI: {entry['ai_distance']} | "
        f"LKH: {entry['lkh_distance']} | "
        f"diff: {entry['difference']}"
    )

if __name__ == "__main__":
    json_paths = ([
    "FinalResults/results15.json",
    "FinalResults/results20.json",
    "FinalResults/results25.json",
    "FinalResults/results30.json",
    "FinalResults/results35.json",
    "FinalResults/results40.json",
    "FinalResults/results45.json",
    "FinalResults/results50.json",
    "FinalResults/results55.json",
    "FinalResults/results60.json",
    "FinalResults/results65.json",
    "FinalResults/results70.json",
    "FinalResults/results80.json",
    "FinalResults/results85.json"
])
print_lkh_comparison_by_size(json_paths)