from pollination_dsl.dag import Inputs, DAG, task, Outputs
from dataclasses import dataclass
from typing import Dict, List
from pollination.honeybee_energy.simulate import SimulateModel
from pollination.honeybee_energy.result import EnergyUseIntensity


# input/output alias
from pollination.alias.inputs.model import hbjson_model_input
from pollination.alias.inputs.ddy import ddy_input
from pollination.alias.inputs.simulation import energy_simulation_parameter_input, \
    measures_input, additional_idf_input, viz_variables_input
from pollination.alias.outputs.eui import parse_eui_results


@dataclass
class AnnualEnergyUseEntryPoint(DAG):
    """Annual energy use entry point."""

    # inputs
    model = Inputs.file(
        description='An energy Model as either a HBJSON, OSM, or IDF.',
        extensions=['hbjson', 'json', 'osm', 'idf'],
        alias=hbjson_model_input
    )

    epw = Inputs.file(
        description='EPW weather file to be used for the annual energy simulation.',
        extensions=['epw']
    )

    ddy = Inputs.file(
        description='A DDY file with design days to be used for the initial '
        'sizing calculation.', extensions=['ddy'],
        alias=ddy_input
    )

    sim_par = Inputs.file(
        description='SimulationParameter JSON that describes the settings for the '
        'simulation.', path='sim-par.json', extensions=['json'], optional=True,
        alias=energy_simulation_parameter_input
    )

    measures = Inputs.folder(
        description='A folder containing an OSW JSON be used as the base for the '
        'execution of the OpenStuduo CLI. This folder must also contain all of the '
        'measures that are referenced within the OSW.', path='measures', optional=True,
        alias=measures_input
    )

    additional_idf = Inputs.file(
        description='An IDF file with text to be appended before simulation. This '
        'input can be used to include large EnergyPlus objects that are not '
        'currently supported by honeybee.', path='additional.idf', extensions=['idf'],
        optional=True, alias=additional_idf_input
    )

    units = Inputs.str(
        description='A switch to indicate whether the data in the final EUI file '
        'should be in SI (kWh/m2) or IP (kBtu/ft2). Valid values are "si" and "ip".',
        default='si', spec={'type': 'string', 'enum': ['si', 'ip']}
    )

    viz_variables = Inputs.str(
        description='Text for EnergyPlus output variables to be visualized on the '
        'geometry in an output view_data HTML report. If unspecified, no view_data '
        'report is produced. Each variable should be in "quotes" and should be '
        'preceded by a -v option. For example\n-v "Zone Air System Sensible Heating '
        'Rate" -v "Zone Air System Sensible Cooling Rate".', default='',
        alias=viz_variables_input
    )

    # tasks
    @task(template=SimulateModel)
    def run_simulation(
        self, model=model, epw=epw, ddy=ddy, sim_par=sim_par,
        measures=measures, additional_idf=additional_idf,
        report_units=units, viz_variables=viz_variables
    ) -> List[Dict]:
        return [
            {'from': SimulateModel()._outputs.hbjson, 'to': 'model.hbjson'},
            {'from': SimulateModel()._outputs.result_folder, 'to': 'run'},
            {'from': SimulateModel()._outputs.result_report, 'to': 'results.html'},
            {'from': SimulateModel()._outputs.visual_report, 'to': 'visual.html'}
        ]

    @task(template=EnergyUseIntensity, needs=[run_simulation])
    def compute_eui(
        self, result_folder=run_simulation._outputs.result_folder, units=units
    ) -> List[Dict]:
        return [
            {'from': EnergyUseIntensity()._outputs.eui_json,
             'to': 'eui.json'}
        ]

    # outputs
    eui = Outputs.file(
        source='eui.json', description='A JSON containing energy use intensity '
        'information across the total model floor area. Values are either kWh/m2 '
        'or kBtu/ft2 depending upon the units input.',
        alias=parse_eui_results
    )

    result_report = Outputs.file(
        description='The HTML report with interactive summaries of energy use, '
        'HVAC component sizes, and other information.', optional=True,
        source='results.html'
    )

    visual_report = Outputs.file(
        description='The HTML report with hourly EnergyPlus output variables '
        'visualized on the geometry.', optional=True,
        source='visual.html'
    )

    sql = Outputs.file(
        source='run/eplusout.sql',
        description='The result SQL file output by the simulation.'
    )

    zsz = Outputs.file(
        source='run/epluszsz.csv', description='The result CSV with the zone loads '
        'over the design day output by the simulation.', optional=True
    )

    html = Outputs.file(
        source='run/eplustbl.htm',
        description='The result HTML page with summary reports output by the simulation.'
    )

    err = Outputs.file(
        source='run/eplusout.err',
        description='The error report output by the simulation.'
    )
