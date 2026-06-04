from __future__ import annotations


def _is_failed_result(entry: dict) -> bool:
    """
    A result is considered failed only if both distance and route
    specifically contain the word 'failed'.
    """
    return (
        str(entry.get("distance")).strip().lower() == "failed"
        and str(entry.get("route")).strip().lower() == "failed"
    )


def summarize_ai_improvement_all(
    results: dict,
    ai_key: str = "AI",
    worse_cutoff_pct: float | None = None,
) -> dict:
    """
    Calculates AI improvement compared to all other heuristics for each file.

    Improvement formula:
        (other_distance - ai_distance) / other_distance * 100

    Positive  => AI is better / shorter distance
    Negative  => AI is worse / longer distance

    Original behavior:
        average_improvement_pct still averages all valid numeric comparisons.

    Additional behavior:
        - failed results are excluded by default
        - if worse_cutoff_pct is given, filtered averages exclude results
          where AI differs by more than that percentage in either direction

    Example:
        worse_cutoff_pct = 25

    excludes from filtered averages:
        improvement_pct < -25
        improvement_pct > 25

    Failed comparison:
        A result is treated as failed if:

            distance == "failed"
            route == "failed"
    """

    full_summary = {}

    improvements_by_heuristic = {}
    filtered_improvements_by_heuristic = {}

    total_excluded_by_cutoff = 0
    total_excluded_by_failed = 0
    failed_occurrences = []

    for filename, heuristics in results.items():

        if ai_key not in heuristics:
            raise KeyError(f"AI key '{ai_key}' not found in {filename}")

        ai_entry = heuristics[ai_key]
        ai_failed = _is_failed_result(ai_entry)

        ai_distance = ai_entry["distance"]

        file_summary = {}
        file_improvements = []
        filtered_file_improvements = []

        file_excluded_by_cutoff = 0
        file_excluded_by_failed = 0

        for heuristic, entry in heuristics.items():
            if heuristic == ai_key:
                continue

            other_failed = _is_failed_result(entry)
            excluded_by_failed = ai_failed or other_failed

            if excluded_by_failed:
                file_excluded_by_failed += 1
                total_excluded_by_failed += 1

                failed_occurrences.append(
                    {
                        "filename": filename,
                        "heuristic": heuristic,
                        "ai_failed": ai_failed,
                        "other_failed": other_failed,
                    }
                )

                file_summary[heuristic] = {
                    "other_distance": entry["distance"],
                    "ai_distance": ai_distance,
                    "improvement_pct": None,
                    "excluded_by_cutoff": False,
                    "excluded_by_failed": True,
                }

                continue

            other_distance = entry["distance"]

            improvement_pct = (
                (other_distance - ai_distance) / other_distance * 100
            )

            excluded_by_cutoff = (
                worse_cutoff_pct is not None
                and abs(improvement_pct) > worse_cutoff_pct
            )

            if excluded_by_cutoff:
                file_excluded_by_cutoff += 1
                total_excluded_by_cutoff += 1

            file_summary[heuristic] = {
                "other_distance": other_distance,
                "ai_distance": ai_distance,
                "improvement_pct": improvement_pct,
                "excluded_by_cutoff": excluded_by_cutoff,
                "excluded_by_failed": False,
            }

            file_improvements.append(improvement_pct)

            if heuristic not in improvements_by_heuristic:
                improvements_by_heuristic[heuristic] = []

            improvements_by_heuristic[heuristic].append(improvement_pct)

            if not excluded_by_cutoff:
                filtered_file_improvements.append(improvement_pct)

                if heuristic not in filtered_improvements_by_heuristic:
                    filtered_improvements_by_heuristic[heuristic] = []

                filtered_improvements_by_heuristic[heuristic].append(improvement_pct)

        file_summary["average_improvement_pct"] = (
            sum(file_improvements) / len(file_improvements)
            if file_improvements
            else None
        )

        file_summary["filtered_average_improvement_pct"] = (
            sum(filtered_file_improvements) / len(filtered_file_improvements)
            if filtered_file_improvements
            else None
        )

        file_summary["num_excluded_by_cutoff"] = file_excluded_by_cutoff
        file_summary["num_excluded_by_failed"] = file_excluded_by_failed

        full_summary[filename] = file_summary

    average_improvement_by_heuristic = {}
    filtered_average_improvement_by_heuristic = {}

    for heuristic, improvements in improvements_by_heuristic.items():
        average_improvement_by_heuristic[heuristic] = (
            sum(improvements) / len(improvements)
            if improvements
            else None
        )

    for heuristic, improvements in filtered_improvements_by_heuristic.items():
        filtered_average_improvement_by_heuristic[heuristic] = (
            sum(improvements) / len(improvements)
            if improvements
            else None
        )

    full_summary["average_improvement_by_heuristic"] = (
        average_improvement_by_heuristic
    )

    full_summary["filtered_average_improvement_by_heuristic"] = {
        "worse_cutoff_pct": worse_cutoff_pct,
        "averages": filtered_average_improvement_by_heuristic,
    }

    full_summary["exclusion_summary"] = {
        "total_excluded_by_cutoff": total_excluded_by_cutoff,
        "total_excluded_by_failed": total_excluded_by_failed,
        "failed_occurrences": failed_occurrences,
    }

    return full_summary


def print_ai_improvement_summary(summary: dict, file=None) -> None:
    averages_by_heuristic = summary.get("average_improvement_by_heuristic", {})

    filtered_summary = summary.get("filtered_average_improvement_by_heuristic", {})
    worse_cutoff_pct = filtered_summary.get("worse_cutoff_pct")
    filtered_averages = filtered_summary.get("averages", {})

    exclusion_summary = summary.get("exclusion_summary", {})
    total_excluded_by_cutoff = exclusion_summary.get("total_excluded_by_cutoff", 0)
    total_excluded_by_failed = exclusion_summary.get("total_excluded_by_failed", 0)
    failed_occurrences = exclusion_summary.get("failed_occurrences", [])

    special_keys = {
        "average_improvement_by_heuristic",
        "filtered_average_improvement_by_heuristic",
        "exclusion_summary",
    }

    file_level_keys = {
        "average_improvement_pct",
        "filtered_average_improvement_pct",
        "num_excluded_by_cutoff",
        "num_excluded_by_failed",
    }

    for filename, file_summary in summary.items():
        if filename in special_keys:
            continue

        print(f"\n{filename}", file=file)
        print("-" * len(filename), file=file)

        for heuristic, values in file_summary.items():
            if heuristic in file_level_keys:
                continue

            if values.get("excluded_by_failed"):
                print(
                    f"{heuristic:8s}: "
                    f"AI distance = {values['ai_distance']}, "
                    f"{heuristic} distance = {values['other_distance']}, "
                    f"improvement = failed "
                    f"[excluded: failed]",
                    file=file,
                )
                continue

            excluded_marker = (
                " [excluded: cutoff]"
                if values["excluded_by_cutoff"]
                else ""
            )

            print(
                f"{heuristic:8s}: "
                f"AI distance = {values['ai_distance']:.2f}, "
                f"{heuristic} distance = {values['other_distance']:.2f}, "
                f"improvement = {values['improvement_pct']:.2f}%"
                f"{excluded_marker}",
                file=file,
            )

        avg = file_summary["average_improvement_pct"]

        if avg is None:
            print("Average improvement for file: No valid values", file=file)
        else:
            print(
                f"Average improvement for file: {avg:.2f}%",
                file=file,
            )

        if worse_cutoff_pct is not None:
            filtered_avg = file_summary["filtered_average_improvement_pct"]

            if filtered_avg is None:
                print(
                    f"Filtered average for file "
                    f"(excluding AI differing more than {worse_cutoff_pct:.2f}%): "
                    f"No values left",
                    file=file,
                )
            else:
                print(
                    f"Filtered average for file "
                    f"(excluding AI differing more than {worse_cutoff_pct:.2f}%): "
                    f"{filtered_avg:.2f}%",
                    file=file,
                )

            print(
                f"Excluded comparisons for file by cutoff: "
                f"{file_summary['num_excluded_by_cutoff']}",
                file=file,
            )

        print(
            f"Excluded comparisons for file by failed result: "
            f"{file_summary['num_excluded_by_failed']}",
            file=file,
        )

    print("\nAverage improvement by heuristic", file=file)
    print("--------------------------------", file=file)

    for heuristic, avg in averages_by_heuristic.items():
        if avg is None:
            print(f"{heuristic:8s}: No valid values", file=file)
        else:
            print(f"{heuristic:8s}: {avg:.2f}%", file=file)

    if worse_cutoff_pct is not None:
        print(
            f"\nFiltered average improvement by heuristic "
            f"(excluding AI differing more than {worse_cutoff_pct:.2f}%)",
            file=file,
        )
        print("--------------------------------------------------------", file=file)

        for heuristic, avg in filtered_averages.items():
            if avg is None:
                print(f"{heuristic:8s}: No valid values", file=file)
            else:
                print(f"{heuristic:8s}: {avg:.2f}%", file=file)

    print("\nExclusion summary", file=file)
    print("-----------------", file=file)

    print(
        f"Total excluded by cutoff: {total_excluded_by_cutoff}",
        file=file,
    )

    print(
        f"Total excluded by failed result: {total_excluded_by_failed}",
        file=file,
    )

    if failed_occurrences:
        print("\nFailed result occurrences", file=file)
        print("-------------------------", file=file)

        for item in failed_occurrences:
            reasons = []

            if item["ai_failed"]:
                reasons.append("AI failed")

            if item["other_failed"]:
                reasons.append(f"{item['heuristic']} failed")

            reason_text = ", ".join(reasons)

            print(
                f"{item['filename']} / {item['heuristic']}: {reason_text}",
                file=file,
            )