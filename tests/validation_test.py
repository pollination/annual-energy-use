from pollination.annual_energy_use.entry import AnnualEnergyUseEntryPoint
from queenbee.recipe.dag import DAG


def test_annual_energy_use():
    recipe = AnnualEnergyUseEntryPoint().queenbee
    assert recipe.name == 'annual-energy-use-entry-point'
    assert isinstance(recipe, DAG)
