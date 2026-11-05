from schedule import make_ics


def test_committed_ics_is_up_to_date():
    assert make_ics.OUT.read_bytes() == make_ics.build().encode("utf-8")


def test_lines_are_folded_and_crlf():
    text = make_ics.build()
    assert text.endswith("\r\n")
    for line in text.split("\r\n"):
        assert len(line.encode("utf-8")) <= 75


def test_every_event_repeats_on_weekdays_with_alarm():
    text = make_ics.build()
    assert text.count("BEGIN:VEVENT") == len(make_ics.BLOCKS)
    assert text.count("RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR") == len(make_ics.BLOCKS)
    assert text.count("BEGIN:VALARM") == len(make_ics.BLOCKS)
