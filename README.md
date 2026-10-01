# Penumbra

An open data index that surfaces the most overlooked municipalities in Bahia,
measured across income, public services, fiscal capacity, and visibility. The
focus is the interior, particularly the cocoa-growing region, tied to the 2026
elections.

## The name

Penumbra is the band of half-light between full shadow and full brightness. Not
the black where nothing is seen, nor the spotlight where everything appears. It
is the in-between, the place where something exists but almost no one notices.
That is what the project names. The municipalities the index surfaces are not
invisible by decree. They are there, with a name, a code, and people, but they
live in a grey zone of public attention, far from the headline and the campaign
trail. There is also the astronomical sense: the penumbra is the edge of an
eclipse, where light is only partially blocked. That is the border this project
tries to map.

## The cocoa zone

The heart of the project is southern Bahia. The cocoa region was once among the
wealthiest in the country and sank into neglect from the late 1980s onward,
when the witches'-broom plague devastated the crop. A controversy persists,
defended by some producers and researchers and still under investigation, that
the fungus was introduced deliberately. This project takes no side in that
dispute. What it does is measure, with data, the depth of the shadow the region
ended up in.

## How the index works

Each municipality receives a score from 0 to 100. The higher the score, the
deeper in the penumbra. The score comes from six signals grouped into three
ideas.

Need deprivation, measured by per-capita income and the combination of HDI,
IDEB, and infant mortality. Fiscal gap, measured by fiscal autonomy, how much
the municipality raises on its own instead of relying on federal transfers. And
invisibility, measured by distance to the state capital, low population density,
and small population size.

Each signal becomes a percentile within the full set of municipalities, which
makes the index resistant to extreme cases like Salvador. A missing data point
receives the median value, never the worst. A municipality that did not report
to the Treasury receives a high score on the fiscal signal, because a lack of
transparency is itself a sign of penumbra. Weights are versioned in
`pipeline/config/pesos.json` and the site also shows a version with equal
weights as a sensitivity check.

## Sources

All data is public and by municipality, keyed by the IBGE code.

- IBGE, municipality list, territorial mesh, 2022 Census, and municipal GDP
- IPEA, Human Development Atlas, HDI, and infant mortality
- INEP, IDEB for early primary education
- National Treasury, SICONFI, revenue, expenditure, and investment

## Structure

```
pipeline/   collects the open data and builds the index (Python)
  src/      one collector per source, plus normalization and scoring
  config/   sources and weights, versioned
app/        site that shows the map, ranking, and municipality profile (Next.js)
  public/data/  indice.json and municipios.geojson, consumed by the site
```

## Run

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

The site deploys on Vercel pointing the root directory to `app`. The data files
are versioned in `app/public/data`, so deployment does not depend on running
the pipeline.

## Note

Independent project with no political affiliation. It does not say who to vote
for. It brings together public data to widen the field of view ahead of the 2026
elections, when the interior tends to fall off the campaign map. The index does
not replace the knowledge of people who live there. It only returns shape to
what was in the half-light.

## License

MIT.
