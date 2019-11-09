import unicode_table

def test_unicode_table(dash_duo):
    app = unicode_table.app
    app.config.external_stylesheets = []
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("tbody > tr > td:nth-child(3)", "BALLOT SCRIPT X", timeout=10)
    assert not dash_duo.get_logs()
