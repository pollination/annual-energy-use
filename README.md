# annual-energy-use

Calculate annual energy use intensity (EUI) for a Honeybee model and optionally
get several HTML reports to visualize the energy use.

The recipe outputs a file called `eui.json` in the format below:

```
{
  "eui": 306.852,
  "total_floor_area": 66129.6,
  "conditioned_floor_area": 66129.6,
  "total_energy": 20292008.333,
  "end_uses": {
    "heating": 30.924,
    "cooling": 84.342,
    "interior_lighting": 27.451,
    "interior_equipment": 164.115,
    "pumps": 0.019
  }
}
```
