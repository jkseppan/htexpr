import unicode_table

def test_unicode_table(dash_duo):
    dash_duo.start_server(unicode_table.app)
    dash_duo.wait_for_text_to_equal("tbody > tr > td:nth-child(3)", "BALLOT SCRIPT X", timeout=10)
    assert not dash_duo.get_logs()
