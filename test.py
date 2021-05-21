def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)


def test_forms(cldf_dataset):
    assert len(list(cldf_dataset["FormTable"])) == 10231
    assert any(f["Form"] == "lʹämoi" for f in cldf_dataset["FormTable"])


def test_parameters(cldf_dataset):
    assert len(list(cldf_dataset["ParameterTable"])) == 313


def test_languages(cldf_dataset):
    assert len(list(cldf_dataset["LanguageTable"])) == 27


def test_cognates(cldf_dataset):
    assert len(list(cldf_dataset["CognateTable"])) == 9751
    assert any(f["Form"] == "tö̆ɣət" for f in cldf_dataset["CognateTable"])
