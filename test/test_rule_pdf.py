import logging
import pytest


import splint.rule_pdf as rule_pdf

logging.getLogger('camelot').setLevel(logging.CRITICAL)

@pytest.mark.parametrize("file, rule_id, status, expected_msg", [
    ("./rule_pdf/RuleId.pdf", "Rule001",True, "Test Result 92%"),
    ("./rule_pdf/RuleId.pdf", "Rule002",True, "Test Result 91%"),
    ("./rule_pdf/RuleId.pdf", "Rule003",False, "TestResult 61%"),
])
def test_extract_tables(file, rule_id, status, expected_msg):
    tables = rule_pdf.extract_tables_from_pdf(file)
    assert tables

    for result in rule_pdf.rule_pdf_rule_id(file, rule_id=rule_id):
        assert result.status is status
        assert result.msg == expected_msg