import re

from app.models import LogAnalysis, LogIssue

TIMESTAMP_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?(?:Z|[+-]\d{2}:?\d{2})?\b")


class LogService:
    """Summarize supplied logs locally without persisting or forwarding them."""

    def analyze(self, logs: str) -> LogAnalysis:
        grouped: dict[str, list[tuple[str | None, str]]] = {}
        lines = logs.splitlines()
        for line in lines:
            category = self._category(line)
            if category:
                timestamp = (match.group(0) if (match := TIMESTAMP_PATTERN.search(line)) else None)
                grouped.setdefault(category, []).append((timestamp, line.strip()))

        issues = [
            LogIssue(
                category=category,
                count=len(entries),
                first_timestamp=next((timestamp for timestamp, _ in entries if timestamp), None),
                last_timestamp=next((timestamp for timestamp, _ in reversed(entries) if timestamp), None),
                example=entries[0][1][:500],
            )
            for category, entries in grouped.items()
        ]
        issue_count = sum(issue.count for issue in issues)
        executive_summary = (
            f"Detected {issue_count} potential error event(s) across {len(issues)} category/categories."
            if issues
            else "No recognized error patterns were found in the supplied logs."
        )
        technical_summary = "; ".join(f"{issue.category}: {issue.count}" for issue in issues) or "No error signatures matched."
        return LogAnalysis(
            lines_analyzed=len(lines),
            executive_summary=executive_summary,
            technical_summary=technical_summary,
            issues=issues,
        )

    @staticmethod
    def _category(line: str) -> str | None:
        normalized = line.lower()
        if "connection refused" in normalized or "econnrefused" in normalized:
            return "Connection refused"
        if "traceback" in normalized:
            return "Python traceback"
        if "fatal" in normalized:
            return "Fatal error"
        if "exception" in normalized:
            return "Exception"
        if re.search(r"\berror\b", normalized):
            return "Error"
        return None
