from datetime import datetime, timezone

from app.data.ngo_links import NGO_DONATION_URLS
from app.schemas import NgoProfile, RegionStat, SourceRecord


DATA_AS_OF = datetime(2026, 7, 26, 0, 0, tzinfo=timezone.utc)


def source(
    title: str,
    organization: str,
    source_type: str,
    url: str,
    reporting_year: int | None = None,
) -> SourceRecord:
    return SourceRecord(
        title=title,
        organization=organization,
        sourceType=source_type,
        url=url,
        reportingYear=reporting_year,
    )


REGIONS = [
    RegionStat(
        id="sudan", name="Sudan", country="Sudan", lat=15.5, lng=30.2,
        crisisType="Armed conflict and displacement", peopleInNeed="Nearly 26 million",
        displacedPeople="Nearly 13 million", fundingStatus="2025 response plans requested US$6 billion",
        focusAreas=["Food security", "Protection", "Shelter", "Health"],
        affectedLocations=["Darfur", "Khartoum", "Kordofan", "Gezira"],
        summary="Conflict has driven mass displacement, disrupted essential services, and increased food insecurity across Sudan and neighbouring countries.",
        sources=[
            source("Sudan emergency", "UNHCR", "Official emergency page", "https://www.unhcr.org/emergencies/sudan-emergency", 2025),
            source("Sudan country updates", "OCHA ReliefWeb", "Humanitarian updates", "https://reliefweb.int/country/sdn"),
        ], asOf=DATA_AS_OF,
    ),
    RegionStat(
        id="gaza", name="Gaza", country="Palestine", lat=31.45, lng=34.4,
        crisisType="Armed conflict and displacement", peopleInNeed="2.1 million",
        displacedPeople="Most of the population has been displaced", fundingStatus="See current OCHA response and funding updates",
        focusAreas=["Health", "Food", "Shelter", "Water and sanitation"],
        affectedLocations=["North Gaza", "Gaza City", "Deir al-Balah", "Khan Younis", "Rafah"],
        summary="Hostilities and access constraints have severely affected health care, shelter, food security, water systems, and civilian protection.",
        sources=[
            source("Occupied Palestinian Territory updates", "UN OCHA", "Official crisis portal", "https://www.ochaopt.org/"),
            source("Palestine humanitarian updates", "OCHA ReliefWeb", "Humanitarian updates", "https://reliefweb.int/country/pse"),
        ], asOf=DATA_AS_OF,
    ),
    RegionStat(
        id="yemen", name="Yemen", country="Yemen", lat=15.6, lng=47.5,
        crisisType="Protracted conflict", peopleInNeed="19.5 million",
        displacedPeople="4.8 million internally displaced", fundingStatus="Humanitarian response remains underfunded",
        focusAreas=["Food security", "Nutrition", "Health", "Protection"],
        affectedLocations=["Marib", "Al Hudaydah", "Taiz", "Hajjah", "Sa'dah"],
        summary="Conflict, economic decline, climate shocks, and disrupted public services continue to drive humanitarian needs.",
        sources=[
            source("Yemen country profile", "UNHCR", "Official country page", "https://www.unhcr.org/where-we-work/countries/yemen", 2025),
            source("Yemen humanitarian updates", "OCHA ReliefWeb", "Humanitarian updates", "https://reliefweb.int/country/yem"),
        ], asOf=DATA_AS_OF,
    ),
    RegionStat(
        id="somalia", name="Somalia", country="Somalia", lat=5.2, lng=46.2,
        crisisType="Climate shocks and displacement", peopleInNeed="Millions require humanitarian assistance",
        displacedPeople="Nearly one in five people is internally displaced", fundingStatus="See linked operational updates",
        focusAreas=["Water", "Food security", "Livelihoods", "Protection"],
        affectedLocations=["Banadir", "Bay", "Lower Shabelle", "Gedo", "Hiraan"],
        summary="Recurrent drought, flooding, conflict, and displacement continue to affect access to food, water, livelihoods, and protection.",
        sources=[
            source("Somalia country profile", "UNHCR", "Official country page", "https://www.unhcr.org/where-we-work/countries/somalia"),
            source("Somalia humanitarian updates", "OCHA ReliefWeb", "Humanitarian updates", "https://reliefweb.int/country/som"),
        ], asOf=DATA_AS_OF,
    ),
    RegionStat(
        id="drc", name="Eastern DRC", country="Dem. Rep. Congo", lat=-3.4, lng=27.2,
        crisisType="Armed conflict and displacement", peopleInNeed="More than 20 million",
        displacedPeople="Millions are internally displaced", fundingStatus="See linked response updates",
        focusAreas=["Protection", "Shelter", "Health", "Food security"],
        affectedLocations=["North Kivu", "South Kivu", "Ituri", "Tanganyika"],
        summary="Armed violence and repeated displacement have disrupted services and increased protection, shelter, health, and food needs.",
        sources=[
            source("Democratic Republic of the Congo", "UNHCR", "Official country page", "https://www.unhcr.org/where-we-work/countries/democratic-republic-congo"),
            source("DRC humanitarian updates", "OCHA ReliefWeb", "Humanitarian updates", "https://reliefweb.int/country/cod"),
        ], asOf=DATA_AS_OF,
    ),
    RegionStat(
        id="afghanistan", name="Afghanistan", country="Afghanistan", lat=33.8, lng=66.1,
        crisisType="Complex emergency", peopleInNeed="More than 20 million",
        displacedPeople="Millions remain displaced or have returned", fundingStatus="See linked response updates",
        focusAreas=["Food security", "Health", "Shelter", "Livelihoods"],
        affectedLocations=["Herat", "Kabul", "Kandahar", "Badghis", "Nangarhar"],
        summary="Economic hardship, climate shocks, displacement, and limits on essential services continue to shape humanitarian needs.",
        sources=[
            source("Afghanistan country profile", "UNHCR", "Official country page", "https://www.unhcr.org/where-we-work/countries/afghanistan"),
            source("Afghanistan humanitarian updates", "OCHA ReliefWeb", "Humanitarian updates", "https://reliefweb.int/country/afg"),
        ], asOf=DATA_AS_OF,
    ),
    RegionStat(
        id="bangladesh", name="Rohingya response", country="Bangladesh", lat=21.42, lng=92.0,
        crisisType="Refugee displacement", peopleInNeed="Refugees and host communities require sustained assistance",
        displacedPeople="Around one million Rohingya refugees in Bangladesh", fundingStatus="See the current joint response plan",
        focusAreas=["Protection", "Food", "Shelter", "Health"],
        affectedLocations=["Cox's Bazar", "Bhasan Char"],
        summary="The protracted Rohingya response requires continued support for refugees and affected host communities.",
        sources=[
            source("Rohingya emergency", "UNHCR", "Operational data portal", "https://data.unhcr.org/en/situations/myanmar_refugees"),
            source("Bangladesh humanitarian updates", "OCHA ReliefWeb", "Humanitarian updates", "https://reliefweb.int/country/bgd"),
        ], asOf=DATA_AS_OF,
    ),
    RegionStat(
        id="sahel", name="Central Sahel", country="Mali", lat=16.4, lng=-3.6,
        crisisType="Conflict and regional displacement", peopleInNeed="Millions across the region require assistance",
        displacedPeople="Displacement spans Mali, Burkina Faso, Niger, and neighbouring states", fundingStatus="See linked regional updates",
        focusAreas=["Protection", "Food security", "Livelihoods", "Shelter"],
        affectedLocations=["Mali", "Burkina Faso", "Niger"],
        summary="Conflict, insecurity, climate pressure, and displacement are affecting communities across the Central Sahel.",
        sources=[
            source("Sahel crisis", "UNHCR", "Official emergency page", "https://www.unhcr.org/emergencies/sahel-crisis"),
            source("Mali humanitarian updates", "OCHA ReliefWeb", "Humanitarian updates", "https://reliefweb.int/country/mli"),
        ], asOf=DATA_AS_OF,
    ),
]

REGIONS.sort(key=lambda crisis: crisis.name)


NGOS = [
    NgoProfile(
        id="islamic-relief", initials="IR", shortName="Islamic Relief", name="Islamic Relief Worldwide",
        descriptor="Faith-based humanitarian and development organization", coverage="38 countries reported in 2024",
        foundedYear=1984, yearsActive=DATA_AS_OF.year - 1984, reportingYear=2024,
        annualIncome="GBP 275.6M", annualExpenditure="GBP 303.8M", reportedReach="14.5M people",
        countriesActive=38, reportedActivity="Emergency, development, and campaigning projects",
        donationUrl=NGO_DONATION_URLS["islamic-relief"],
        accent="#167b66", acceptedGivingTypes=["Zakat", "Sadaqah", "General donation"],
        focusAreas=["Food", "Shelter", "Health", "Water", "Livelihoods", "Protection"],
        crisisIds=["sudan", "gaza", "yemen", "somalia", "afghanistan", "bangladesh", "sahel"],
        sources=[
            source("Our history", "Islamic Relief Worldwide", "Official history page", "https://islamic-relief.org/about-us/our-history/"),
            source("2024 annual results", "Islamic Relief Worldwide", "Official annual-report summary", "https://islamic-relief.org/news/2024-islamic-relief-spent-more-than-ever-before-to-support-the-worlds-most-vulnerable/", 2024),
            source("Annual reports", "Islamic Relief Worldwide", "Official annual-report index", "https://islamic-relief.org/about-us/annual-reports/", 2024),
        ], asOf=DATA_AS_OF,
    ),
    NgoProfile(
        id="human-appeal", initials="HA", shortName="Human Appeal", name="Human Appeal",
        descriptor="Humanitarian and development organization", coverage="30 countries reported in 2024",
        foundedYear=1991, yearsActive=DATA_AS_OF.year - 1991, reportingYear=2024,
        reportedReach="6.24M people", countriesActive=30,
        reportedActivity="Emergency, development, and seasonal projects", accent="#d8893d",
        donationUrl=NGO_DONATION_URLS["human-appeal"],
        acceptedGivingTypes=["Zakat", "Sadaqah", "General donation"],
        focusAreas=["Food", "Health", "Shelter", "Water", "Orphan support"],
        crisisIds=["sudan", "gaza", "yemen", "somalia", "afghanistan"],
        sources=[
            source("Annual reports", "Human Appeal", "Official annual-report index", "https://humanappeal.org.uk/about-us/annual-reports", 2024),
            source("Where we work", "Human Appeal", "Official programme pages", "https://humanappeal.org.uk/appeals"),
        ], asOf=DATA_AS_OF,
    ),
    NgoProfile(
        id="care", initials="CA", shortName="CARE", name="CARE",
        descriptor="Global humanitarian and development organization", coverage="121 countries reported in 2024",
        foundedYear=1945, yearsActive=DATA_AS_OF.year - 1945, reportingYear=2024,
        reportedReach="53M people", countriesActive=121, reportedActivity="1,450+ projects and initiatives",
        donationUrl=NGO_DONATION_URLS["care"],
        accent="#b95d3d", acceptedGivingTypes=["General donation"],
        focusAreas=["Food", "Health", "Livelihoods", "Gender equality", "Emergency response"],
        crisisIds=["sudan", "gaza", "drc", "somalia", "afghanistan", "sahel"],
        sources=[
            source("CARE 2024 annual report", "CARE", "Official annual report", "https://www.care.org/resources/care-2024-annual-report/", 2024),
            source("CARE FAQs", "CARE", "Official organization profile", "https://www.care.org/about-us/faqs/"),
        ], asOf=DATA_AS_OF,
    ),
    NgoProfile(
        id="mercy-corps", initials="MC", shortName="Mercy Corps", name="Mercy Corps",
        descriptor="Global humanitarian and resilience organization", coverage="46 countries reported in 2024",
        foundedYear=1979, yearsActive=DATA_AS_OF.year - 1979, reportingYear=2024,
        reportedReach="38M people", countriesActive=46, reportedActivity="Humanitarian and resilience programmes",
        donationUrl=NGO_DONATION_URLS["mercy-corps"],
        accent="#327fa1", acceptedGivingTypes=["General donation"],
        focusAreas=["Food", "Water", "Livelihoods", "Cash assistance", "Climate resilience"],
        crisisIds=["sudan", "gaza", "drc", "somalia", "afghanistan", "sahel"],
        sources=[
            source("2024 annual impact summary", "Mercy Corps", "Official annual impact report", "https://www.mercycorps.org/annual-reports/2024", 2024),
            source("Why give to Mercy Corps", "Mercy Corps", "Official organization profile", "https://www.mercycorps.org/en-gb/who-we-are/why-give"),
        ], asOf=DATA_AS_OF,
    ),
    NgoProfile(
        id="save-the-children", initials="SC", shortName="Save the Children", name="Save the Children International",
        descriptor="Child-focused humanitarian and development organization", coverage="113 countries reported in 2024",
        foundedYear=1919, yearsActive=DATA_AS_OF.year - 1919, reportingYear=2024,
        reportedReach="113.6M children", countriesActive=113, reportedActivity="112 emergencies responded to",
        donationUrl=NGO_DONATION_URLS["save-the-children"],
        accent="#c64132", acceptedGivingTypes=["General donation"],
        focusAreas=["Child protection", "Health", "Nutrition", "Education", "Emergency response"],
        crisisIds=["sudan", "gaza", "yemen", "somalia", "drc", "afghanistan", "bangladesh", "sahel"],
        sources=[
            source("Our impact in 2024", "Save the Children International", "Official impact report", "https://www.savethechildren.net/stories/our-impact-2024", 2024),
            source("Our history", "Save the Children International", "Official history page", "https://www.savethechildren.net/about-us/our-history"),
        ], asOf=DATA_AS_OF,
    ),
]

NGOS.sort(key=lambda ngo: ngo.name)
