# Superstore Seasonality — Power BI Build Spec

**Business question:** When does revenue actually arrive, which categories drive the swing, and what should we do about the four-month dead zone?
**Audience:** Commercial / merchandising leadership.
**Decision it informs:** Where to place Q1 demand-generation spend and how to phase Furniture inventory.

---

## 1. Load

Get Data → Text/CSV → load all six files from `data/`:

| File | Rows | Role |
|---|---|---|
| `fact_sales.csv` | 9,799 | Fact — 1 row = one product line on one order |
| `dim_date.csv` | 1,466 | Date dimension, 2015-01-01 → 2019-01-05 |
| `dim_customer.csv` | 793 | Customer + Segment |
| `dim_product.csv` | 1,861 | Product → Sub-Category → Category |
| `dim_geography.csv` | 628 | Postal → City → State → Region |
| `dim_shipmode.csv` | 4 | Ship mode + speed rank |

All keys are pre-cleaned and referentially complete — **zero orphan rows** in any dimension.

## 2. Model

Star schema. All relationships **many-to-one, single direction**, fact → dim.

```
              dim_date
                 ▲  ▲
    OrderDateKey │  │ ShipDateKey (INACTIVE)
                 │  │
dim_customer ◄── fact_sales ──► dim_product
                 │  │
                 ▼  ▼
        dim_geography  dim_shipmode
```

Required model settings:
1. **Mark `dim_date` as date table** on `[Date]`.
2. `dim_date[MonthName]` → Sort by column → `MonthNo`.
3. `dim_date[YearMonth]` → Sort by column → `MonthSort`.
4. `fact_sales[ShipDateKey] → dim_date[DateKey]` must be **inactive** (Power BI allows only one active date link). It powers `[Sales by Ship Date]`.
5. Hide all `*Key` columns from report view.
6. Create a blank table `_Measures`, paste in `DAX_measures.txt`.

## 3. Page layout

### Page 1 — "When does revenue arrive?" (executive)
KPI cards top-left, trend next, breakdowns below. Reviewer decides in 30 seconds.

| Position | Visual | Fields |
|---|---|---|
| Top row, 4 cards | Card | `[Total Sales]`, `[Order Count]`, `[Peak Share %]`, `[Dead Zone Gap to Flat]` — each with `[YoY %]` as the subtitle |
| Row 2, full width | **Column chart** — X `dim_date[MonthName]`, Y `[Total Sales]`, data label `[Share of Total %]` | Title: *"Sep, Nov and Dec generate 43% of annual revenue — Feb generates 2.6%"* |
| Row 3, left | **Line chart** — X `dim_date[YearMonth]`, Y `[Total Sales]` + `[Sales 3M Rolling Avg]` | Title: *"Revenue grew 14.6% CAGR, but the shape of the year barely moved"* |
| Row 3, right | **Matrix heatmap** — rows `dim_date[MonthName]`, columns `dim_product[Category]`, values `[Seasonal Index]`, background conditional formatting diverging on 1.00 | Title: *"Furniture swings hardest: 2.00 in Dec vs 0.26 in Feb"* |

Slicers (top strip, horizontal): Year · Category · Segment · Region.

### Page 2 — "What drives the peak?"
| Visual | Fields |
|---|---|
| Two column charts, side by side | Left: `dim_date[MonthName]` × `[Order Count]`. Right: `dim_date[MonthName]` × `[Median Order Value]` |
| Title across both | *"The peak is a traffic event, not a bigger-basket event"* |
| Bar chart, sorted desc | `dim_product[SubCategory]` × `[Total Sales]`, with `[Peak Share %]` as a second column in a table beside it |
| Table | Sub-Category · `[Total Sales]` · `[Order Count]` · `[Seasonal Swing]` · `[Peak Share %]` |

### Page 3 — "The Jan–Apr dead zone" (decision page)
| Visual | Fields |
|---|---|
| Card | `[Dead Zone Gap to Flat]` — the size of the prize, per year |
| Clustered bar | `dim_date[DeadZone]` × `[Total Sales]` and `[Active Customers]` |
| Matrix | `dim_customer[Segment]` rows × `dim_date[MonthName]` columns × `[Seasonal Index]` |
| Map (filled) | `dim_geography[State]` × `[Peak Share %]` — East over-indexes at 50.7% |

Drill-through from any Category/Sub-Category visual → a product detail page filtered on `dim_product[ProductName]`.

## 4. Formatting rules
- **Colourblind-safe palette:** peak `#0072B2` (blue), positive `#009E73` (green), negative/annotation `#D55E00` (orange), context `#BBBBBB` (grey).
- Colour encodes meaning only — grey is for context. Never rainbow a category axis.
- Every visual title states the **finding**, not the variable.
- Sort every bar chart by value, except month axes, which stay chronological.
- No pie charts, no dual axes, no 3D.
- Currency format `$#,0;($#,0)`, percentages to 1 decimal.

## 5. Known model limitations
Carry this on a text box at the bottom of Page 1:

> Source data contains no Quantity, Discount, Profit or Cost. This model measures **revenue only** — it cannot show margin, discount effectiveness, or whether a revenue rise came from volume or price. Alaska and Hawaii are absent. 2018 is the last complete year.
