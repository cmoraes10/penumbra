# Penumbra

An open data index that maps the municipalities of Bahia most overlooked at once
by income, public services, fiscal capacity, and attention. The focus is the
interior, and especially the cocoa zone, with an eye on the 2026 elections.

## Where the name comes from

Penumbra is the band of half-light between total shadow and full brightness. Not
the pitch dark, where nothing can be seen, nor the full glare of a spotlight,
where everything appears. It is the in-between, the place where something exists
but almost nobody notices. That is the state this project wanted to name. The
municipalities the index illuminates are not invisible by decree; they are there,
with a name, a code, and people, but they live in a grey zone of public attention,
far from the headline and the campaign agenda. There is also the astronomical
meaning: the penumbra is the edge of an eclipse, where light is only partially
blocked. That edge is what the project tries to map.

## The cocoa zone

The heart of the project is the south of Bahia. The cocoa region was once among
the richest in the country and sank into neglect from the late 1980s onward, when
the witches' broom fungus devastated the crop. A controversy persists, defended
by some producers and researchers and still under investigation, that the fungus
may have been introduced deliberately. The project takes no side in that dispute.
What it does is measure, with data, the depth of the shadow the region ended up in.

## How the index works

Each municipality receives a score from 0 to 100. The higher the score, the
deeper in the penumbra. The score comes from six signals grouped into three ideas.

Deprivation of need, measured by income per capita and a combination of HDI,
IDEB, and infant mortality. Lack of own fiscal resources, measured by fiscal
autonomy, the share of revenue the city raises on its own instead of depending
on federal transfers. And invisibility, measured by distance to the capital,
low density, and small population.

Each signal becomes a percentile rank within the municipality set, which makes
the index resistant to extreme cases like Salvador. A missing value receives the
median, never the worst. A municipality that did not report to the Treasury
receives a high score on the fiscal signal, because lack of transparency is
itself a sign of penumbra. Weights are versioned in `pipeline/config/weights.json`
and the site also shows a version with equal weights as a sensitivity check.

## Sources

All data is public and at the municipality level, keyed by IBGE code.

- IBGE, municipality list, territorial mesh, 2022 Census, and municipal GDP
- IPEA, Human Development Atlas, HDI and infant mortality
- INEP, primary school IDEB
- National Treasury, SICONFI, revenues, expenses, and investment

## Structure

```
pipeline/   collects open data and builds the index (Python)
  src/      one collector per source, plus normalisation and calculation
  config/   sources and weights, versioned
app/        site that shows the map, ranking, and municipality profile (Next.js)
  public/data/  index.json and municipios.geojson, consumed by the site
```

## How to run

The pipeline generates the data. Tested with Python 3.12.

```bash
cd pipeline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

The site displays the data. Tested with Node 20.

```bash
cd app
npm install
npm run dev
```

## Deploy

The site deploys on Vercel pointing the root directory at `app`. The data is
already versioned in `app/public/data`, so the deploy does not depend on running
the pipeline.

## Disclaimer

Independent project with no partisan affiliation. It does not tell anyone who to
vote for. It gathers public data to broaden the field of view ahead of the 2026
elections, when the interior tends to stay off the itinerary. The index does not
replace the knowledge of those who live there; it only gives outline to what was
in the half-light.

## Author

Built by Cauã Moraes. Other projects at [mowaveone.com](https://mowaveone.com).
