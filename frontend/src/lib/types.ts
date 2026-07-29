export type SourceRecord = {
  title: string;
  organization: string;
  sourceType: string;
  url: string;
  reportingYear?: number;
};

export type RegionStat = {
  id: string;
  name: string;
  country: string;
  lat: number;
  lng: number;
  crisisType: string;
  peopleInNeed: string;
  displacedPeople: string;
  fundingStatus: string;
  focusAreas: string[];
  affectedLocations: string[];
  summary: string;
  sources: SourceRecord[];
  asOf: string;
};

export type Ngo = {
  id: string;
  initials: string;
  shortName: string;
  name: string;
  descriptor: string;
  coverage: string;
  foundedYear: number;
  yearsActive: number;
  reportingYear: number;
  annualIncome?: string;
  annualExpenditure?: string;
  reportedReach: string;
  countriesActive: number;
  reportedActivity?: string;
  donationUrl: string;
  accent: string;
  acceptedGivingTypes: string[];
  focusAreas: string[];
  crisisIds: string[];
  sources: SourceRecord[];
  asOf: string;
};
