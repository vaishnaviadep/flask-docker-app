def test_controlled_failing_pipeline_scenario():
    expected_status = "completed"
    actual_status = "pending"
    assert actual_status == expected_status, "Intentional failure for CI demo"