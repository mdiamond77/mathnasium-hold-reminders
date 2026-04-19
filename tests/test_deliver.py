from deliver import build_html


SAMPLE_HOLDS = [
    {
        "name": "Alice Smith",
        "hold_end_date": "4/30/2026",
        "guardian_name": "Amy Smith",
        "guardian_phone": "(201) 555-0001",
        "guardian_email": "amy@example.com",
    }
]


def test_build_html_contains_student_name():
    html = build_html("Teaneck", "April 2026", SAMPLE_HOLDS)
    assert "Alice Smith" in html


def test_build_html_contains_hold_end_date():
    html = build_html("Teaneck", "April 2026", SAMPLE_HOLDS)
    assert "4/30/2026" in html


def test_build_html_contains_guardian_info():
    html = build_html("Teaneck", "April 2026", SAMPLE_HOLDS)
    assert "Amy Smith" in html
    assert "(201) 555-0001" in html
    assert "amy@example.com" in html


def test_build_html_contains_center_name():
    html = build_html("Englewood", "April 2026", [])
    assert "Englewood" in html


def test_build_html_contains_hold_reminder():
    html = build_html("Teaneck", "April 2026", [])
    assert "going on hold" in html


def test_build_html_is_valid_html():
    html = build_html("Teaneck", "April 2026", SAMPLE_HOLDS)
    assert html.strip().startswith("<html")
    assert "</html>" in html
