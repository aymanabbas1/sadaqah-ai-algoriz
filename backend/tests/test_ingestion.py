from app.ingestion.extractors import parse_ngo_facts


def test_mercy_corps_extractor_reads_published_impact() -> None:
    text = "In 2025 Mercy Corps reached 37 million people across 35 countries with lifesaving care."
    facts = parse_ngo_facts("mercy_corps", text, {"reporting_year": 2025})
    assert facts["reported_reach"] == "37M people"
    assert facts["countries_active"] == 35


def test_save_the_children_extractor_reads_published_impact() -> None:
    text = (
        "OUR IMPACT FOR CHILDREN IN 2025 37.8 million children reached "
        "92 countries where we worked 113 emergencies responded to"
    )
    facts = parse_ngo_facts("save_the_children", text, {"reporting_year": 2025})
    assert facts["reported_reach"] == "37.8M children"
    assert facts["countries_active"] == 92
    assert facts["reported_activity"] == "113 emergencies responded to"
