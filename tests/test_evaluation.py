from evaluation.evaluate import evaluate


def test_extraction_quality_does_not_regress():
    _, resume_prf, jd_prf, cls, sec, proj, _ = evaluate()
    assert resume_prf[0] >= 0.95 and resume_prf[1] >= 0.9   # precision, recall
    assert jd_prf[0] >= 0.95 and jd_prf[1] >= 0.95
    assert cls[0] == cls[1]
    assert sec[0] == sec[1]
    assert proj[0] == proj[1]
