from dataclasses import dataclass


@dataclass
class PaginationWindow:
    total_pages: int
    pages: list[int]
    have_prev: bool
    have_next: bool
    next_page: int
    prev_page: int


def build_pagination_window(
    page: int,
    total: int,
    page_size: int = 10,
    window_size: int = 3,
) -> PaginationWindow:
    if page_size <= 0 or window_size <= 0:
        raise ValueError("Page size and window size must be greater than 0")

    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))

    half = window_size // 2
    start = max(1, page - half)
    end = start + window_size - 1

    if end > total_pages:
        end = total_pages
        start = max(1, end - window_size + 1)
    
    pages = list(range(start, end + 1))

    have_prev = page > 1
    have_next = page < total_pages

    return PaginationWindow(
        total_pages=total_pages,
        pages=pages,
        have_prev=have_prev,
        have_next=have_next,
        prev_page=page - 1 if have_prev else 1,
        next_page=page + 1 if have_next else total_pages,
    )