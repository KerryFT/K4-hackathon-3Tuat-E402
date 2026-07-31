def requests_impersonation_or_cheating(message: str) -> bool:
    normalized = message.casefold()
    signals = (
        "làm bài hộ",
        "giải hộ bài",
        "giải giúp bài",
        "làm giúp bài",
        "thi hộ",
        "đáp án để nộp",
        "giả làm tôi",
        "nộp bài hộ",
    )
    return any(signal in normalized for signal in signals)

