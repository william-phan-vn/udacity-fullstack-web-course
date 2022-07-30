def paging(page_key: int, page_size: int) -> [int, int]:
    start = (page_key - 1) * page_size
    end = start + page_size
    return start, end
