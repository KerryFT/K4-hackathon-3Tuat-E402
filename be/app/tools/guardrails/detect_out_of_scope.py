OFF_TOPIC_KEYWORDS = (
    "thời tiết",
    "dự báo",
    "nấu ăn",
    "nấu món",
    "món ăn",
    "món gì",
    "ăn món",
    "ăn gì",
    "công thức nấu",
    "quán ăn",
    "giá vàng",
    "tỷ giá",
    "chứng khoán",
    "mua xe",
    "mua sắm",
    "bóng đá",
    "kqbd",
    "thể thao",
    "kết quả bóng đá",
    "xem phim",
    "bài hát",
    "ca sĩ",
    "hát",
    "ca hát",
    "nghe nhạc",
    "âm nhạc",
    "giải trí",
    "xem tivi",
    "bài thơ",
    "làm thơ",
    "truyện cười",
    "tâm sự tình yêu",
    "bói toán",
    "tử vi",
    "lotto",
    "vé số",
    "game online",
    "chơi game",
    "quần áo",
    "thời trang",
    "du lịch",
    "đặt khách sạn",
    "vé máy bay",
)

TRICK_OR_INJECTION_KEYWORDS = (
    "system prompt",
    "systemprompt",
    "system_prompt",
    "promtp",
    "câu lệnh hệ thống",
    "hướng dẫn hệ thống",
    "lời nhắc hệ thống",
    "quy tắc hệ thống",
    "ignore previous instructions",
    "bỏ qua quy tắc",
    "làm ngơ quy tắc",
    "bỏ qua hướng dẫn",
    "forget all instructions",
    "developer mode",
    "chế độ developer",
    "jailbreak",
    "act as",
    "giả làm",
    "đóng vai",
    "quên hết quy tắc",
)

DANGEROUS_OR_ILLEGAL_KEYWORDS = (
    "nổ",
    "chế tạo nổ",
    "chất nổ",
    "thuốc nổ",
    "bom",
    "chế tạo bom",
    "chế bom",
    "chế chất độc",
    "chất độc",
    "vũ khí",
    "chế tạo vũ khí",
    "súng",
    "hack hệ thống",
    "tấn công mạng",
    "bất hợp pháp",
    "ma túy",
    "chất cấm",
    "đánh bạc",
    "cá độ",
)


def is_dangerous_or_illegal(message: str) -> bool:
    """Checks if a user message requests dangerous, illegal, or explosive material instructions."""
    normalized = message.casefold().strip()
    return any(keyword in normalized for keyword in DANGEROUS_OR_ILLEGAL_KEYWORDS)


def is_prompt_injection_or_trick(message: str) -> bool:
    """Checks if a user message attempts prompt extraction, jailbreaking, or tricking the AI agent."""
    normalized = message.casefold().strip()
    return any(keyword in normalized for keyword in TRICK_OR_INJECTION_KEYWORDS)


def is_off_topic_query(message: str) -> bool:
    """Checks if a user message is an off-topic question unrelated to VLearn course/learning curriculum."""
    normalized = message.casefold().strip()

    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in normalized:
            return True

    return False


def detect_out_of_scope(source_count: int) -> bool:
    """Returns True if no relevant sources were retrieved from lecture materials."""
    return source_count == 0



