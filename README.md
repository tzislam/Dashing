# Dashing
A programmable and extenddable framework for understanding the resource utilization behaviors of HPC applications, especially while scaling on a node.

# About
Many HPC application scientists create their own in-house tools for the analysis and visualization of the performance of their scientific applications. Towards this goal, we present Dashing--a framework of interpretable machine learning techniques for understanding the resource utilization behaviors of HPC applications and conducting quantitative comparison of performance between applications. Dashing provides a highly configurable ML pipeline, present the breakdown of factors impacting the on-node scalability of applications in an intuitively hierarchical format. Provided with performance metrics in HDF5 or CSV format, Dashing can generate analysis reports, performance statistics and several visualizations to assist with optimizing any application.

## Preparing the environment

The package manager tool [conda](https://anaconda.org/anaconda/python) is recommended by this framework.  
To automatically install the conda environment needed for this framework, use the command:
```bash
$ conda env create -f environemnt.yml
```
To activate the conda environment, use:
```bash
$ conda activate analysis_framework_env
```

# Collecting data (Optional)

## Using perf-dump

Dashing was designed around using perf-dump and supports loading performance counter data directly from the output from perf-dump.

1. Collect performance data about an application using [perf-dump](https://github.com/tzislam/perf-dump)
2. Store that data in the `data/` directory, in the following structure:

```
data/
+-- app_name/
|   +-- jobs/
|   |  +-- 00/
|   |  |  +-- perf-dump.1.h5
|   |  |  +-- perf-dump.2.h5 ...
|   |  +-- 01/
|   |  |  +-- perf-dump.1.h5
|   |  |  +-- perf-dump.2.h5
|   |  +-- 02/ ...
|   +-- groups/
|   |  +-- papi_native_counters.txt.00
|   |  +-- papi_native_counters.txt.01
|   |  +-- papi_native_counters.txt.02 ...

```

## Using other tools

Dashing supports performance data collected with any tool as long as the input to the framework is structured in the following specified format. The input file must be in CSV format. The CSV must be formatted such that each column denotes a region and each row denotes a performance counter. Each entry is a list of floats delimented by commas, these values denotes the average counter value for each processor configuration.

```
,reg1_name,reg2_name,reg3_name
event_name,"avg_data1_for_process1_thread1_for_reg1,avg_data2_for_process1_thread2_for_reg1,avg_data3_for_process2_thread1_for_reg1,avg_data4_for_process2_thread2_for_reg1","avg_data1_for_process1_thread1_for_reg2,avg_data2_for_process1_thread2_for_reg2,avg_data3_for_process2_thread1_for_reg2,avg_data4_for_process2_thread2_for_reg2","avg_data1_for_process1_thread1_for_reg3,avg_data2_for_process1_thread2_for_reg3,avg_data3_for_process2_thread1_for_reg3,avg_data4_for_process2_thread2_for_reg3"
```

Following is an example csv file included in the data/test_data directory in the repository.

```
#Example in data/test_data/test.csv
,reg1_name,reg2_name,reg3_name
OFFCORE_REQUESTS:ALL_DATA_RD,"1,2,3,4","32,34,24,34","2,3,4,5"
BR_MISP_EXEC:ALL_INDIRECT_JUMP_NON_CALL_RET,"2,5,1,0","34,34,34,534","3,4,1,5"
PAGE_WALKER_LOADS:EPT_ITLB_MEMORY,"3,100,3,5","34,53,43,3","3,0,10,34"
DTLB_STORE_MISSES:WALK_COMPLETED_4K,"2,452,42,45","342,42,43,6","342,23,230,21"
Runtime,"32,42,34,40","33,43,13,43","323,232,2109,100"
```


# Configuring

1. Edit or create a new yaml file, which will be used to configure the pipeline to your needs. The yaml file must be formatted in the same fashion as the examples provided. Try editing `configs/global.yml` to get an idea of the structure.
2. Each app's configuration must contain the following information:
	* data: path to the directory containing perf-dump files.
	* tasks: a list of functions that must be run. modules.resource_score.compute_rsm_task_all_regions must be first in order to generate rsm data
	* rsm_use_nn_solver: True/False. Ideally, you should only use the value True.
	* name: The name of this application, or any string to refer to the dataset for a particular application.
	* procs: (optional) specify which processes you want to analyze. For e.g., if you collected configurations such as 1 thread, 2 threads, 4 threads, 8 threads, 32 threads, then specify 1,2,4,8,32. If not specified, all processes will be analyzed (1,2,3,4,5....32). These numbers are used to construct the files that will be read in for analysis. The framework skips files that cannot be found.

	### Example for Nyx
```yaml
	nyx_rsm:
		data: 'data/nyx_data/jobs/'
		rsm_use_nn_solver: True
		name: 'Nyx'
		tasks:
			- modules.resource_score.compute_rsm_task_all_regions
			- viz.barchart.create_barchart
			- viz.heatmap.create_heatmap
			- viz.sunburst.sunburst
```

3. Comparing applications works slightly differently. These must be specified:
	* tasks: a list of other configs (e.g. iamr_32, incflo_32) to load, followed by a list of comparative visualizations.
	* compat_pairs: a list of perf-dump regions to compare, in the format:
		** config_name:region_name,another_config:another_region
	* arch: haswell/knl
	* data_rescale:
	* rsm_iters:
	* rsm_print: print raw values (debug)
	* rsm_use_nn_solver:
	* port: port for the url address for the dashboard (allows you to run multiple dashboards with different configs simultaneously)

	### Example for a comparative config
	This generates rsm data for 4 apps, computes comparisons, and creates a dashboard to visualize it all. In this example, `NavierStokes::advance()` is the exact name of a region that was annotated and captured from IAMR's performance data.

```yaml
main:
	arch: haswell
	data_rescale: True
	rsm_iters: 5
	rsm_print: True
	rsm_use_nn_solver: False
	port: 7500

	tasks:
		- warpx
		- iamr
		- incflo_32
		- incflo_64
		- incflo_128
		- nyx
		- modules.compatibility_score.compat_task
		- viz.res_compat_graph.create_res_versus_compat_graph
		- viz.dashboard.dashboard_init

	compat_pairs:
		- iamr:MLABecLaplacian::Fsmooth(),incflo_32:MLEBABecLap::Fsmooth()
		- iamr:MLABecLaplacian::Fsmooth(),incflo_64:MLEBABecLap::Fsmooth()
		- iamr:MLABecLaplacian::Fsmooth(),incflo_128:MLEBABecLap::Fsmooth()
		- iamr:NavierStokes::advance(),incflo_32:incflo::Advance
		- iamr:NavierStokes::advance(),incflo_64:incflo::Advance
		- iamr:NavierStokes::advance(),incflo_128:incflo::Advance
```

### List of visualizations available:

##### Modules
1. `modules.resource_score.compute_rsm_task_all_regions`
	* This must be the first function called in order to generate rsm data for any following analyses.
2. `modules.compatibility_score.compat_task`
	* This must be called before comparative visualizations can be made.
3. `viz.dashboard.dashboard_init`
	* This must be the last function called in order to generate the dashboard for visulizations.

##### Analyzing a single application:
1. `viz.heatmap.create_heatmap`
	* Compares the RSM scores of resources per region, giving a broad overview about which resources are heavily used by which regions.
2. `viz.sunburst.sunburst`
	* Presents a large volume of hierarchical data in an intuitive visualization. A single sunburst chart represents an application. Moving outwards, the next circle represents the contribution of each region to the overall execution time of the application. Then, the importance of each resource that contributes to explaining the efficiency loss of its parent region. Finally, the importance of each hardware counter that contributes to its respective resource.
3. `viz.linechart.raw_values_per_proc_config`
	* Shows the values of hardware counters normalized within a region, as an application scales.
4. `viz.barchart.create_rsm_error_barchart`
	* Compares the normalized RSM scores of each resource per region.
5. `viz.barchart.load_imbalance`
	* A stacked barchart showing the load of each process for each configuration of process counts, useful for identifying load imbalances as the application scales.

##### Analysis across multiple applications:
1. `viz.res_compat_graph.create_res_versus_compat_graph`
	* A scatterplot comparing the performance profiles between two applications. To configure which pairs of regions to compare, a separate list must be created called `compat_pairs`. See "Example for a comparative config" above.
2. `viz.compat_barchart.compat_barchart`
	* Compares the performance profiles between two applications. Configured in the same manner as above.

#### Notes
* If a setting is specified in both a global config and an app config, the app's version will overwrite the global's.


# Running

Specify the file containing the config you want to run, then the name of that config. If the name is not provided, `main` is used by default.

```bash
python driver.py configs/example_config.yml
```

# Extending the Pipeline
Dashing was designed to support the modular addition of vizualizations, data processing, analyses, and other functionality.

## DataLoader
`DataLoader` is the backbone of Dashing. This object is initialized in `driver.py` and is passed between every module.

### Caching
For any configuration, a unique key is generated using the configuration file name and the specific configuration name. This key maps to a cached pkl of DataLoader which is dumped between each module. This allows for computationally difficult modules to be cached for future runs.

To force Dashing to regenerate the cached file, include `-f` while calling `driver.py`.

Example:
```bash
python driver.py -f my_config_file.yaml
```

### Passing Data
As `DataLoader` is passed around, all data to be shared with other modules should be stored and retrieved from `DataLoader`. `DataLoader` uses a dictionary for this purpose which can directly be subscriptable. For all intents and purposes, `DataLoader` can be interacted with as if it was a dictionary.

**Example:**

```
data_loader['key1'] = 32
...
print(data_loader['key1']) // 32
```

### Methods

#### get_app_data(reg, rescale=False, keys=None)
**Inputs:**  
`reg` -- string denoting the region name  
`rescale` -- boolean denoting whether the data should be normalized to be within [0, 1]  
`keys` -- List of hardware events to return data on. If left as default value `None`, uses all hardware events.

**Output:**  
An mxn numpy array where m is the number of processor configurations and n is the number of hardware events whose entries are the performance data collected for that region. 

#### get_app_dict(reg, rescale=False, keys=None)
**Inputs:**  
See `get_app_data`

**Output:**  
A dictionary whose keys are hardware events and values are mx1 numpy arrays where m is the number of processor configurations and whose entries are the performance data collected for that region.

#### get_app_eff_loss(reg)
**Inputs:**  
`reg` -- string denoting the region name

**Outputs:**  
A mx1 numpy array whose entries are the effeciency loss for each processor configuration.

#### get_events()

**Outputs:**  
List of string whose values are the hardware events for the dataset.

#### get_regions()

**Outputs:**  
List of string whose values are the regions for the dataset.

#### get_config_name()

**Outputs:**  
String denoting the configuration name


## Modules

There exists two types of modules that may be specified in a configurations: *Local* and *Global*

Local tasks are methods that expect a single `DataLoader` object to be passed in. Global tasks are methods that expect a `dict` object whose keys are local config names and whose valuess are their respective `DataLoader` objects.

In the following example, this specifies a function named `example_func` defined in `modules/example_file.py`. Modules may be placed anywhere.
```
example_config:
	...
	tasks:
		- modules.example_file.example_func
```

# Analysis Scenarios and commands

# Future extensions

# Reference

Refer to the following TWO papers if you make use of any part of the Dashing framework:

@INPROCEEDINGS{islam2019toward,
  author={Islam, Tanzima Z. and Ayala, Alexis and Jensen, Quentin and Ibrahim, Khaled Z.},
  booktitle={2019 IEEE/ACM International Workshop on Programming and Performance Visualization Tools (ProTools)}, 
  title={Toward a Programmable Analysis and Visualization Framework for Interactive Performance Analytics}, 
  year={2019},
  pages={70-77}}

@INPROCEEDINGS{islam2016a,
  author={Islam, Tanzima Z. and Thiagarajan, Jayaraman J. and Bhatele, Abhinav and Schulz, Martin and Gamblin, Todd},
  booktitle={SC '16: Proceedings of the International Conference for High Performance Computing, Networking, Storage and Analysis}, 
  title={A Machine Learning Framework for Performance Coverage Analysis of Proxy Applications}, 
  year={2016},
  pages={538-549}}



# Authors
* [Tanzima Islam](https://github.com/tzislam)
* [Alex Ayala](https://github.com/S-Toad/)
* [Quentin Jensen](https://github.com/jensenq)


# Acknowledgments
* Dr. Khaled Ibrahim
* Dr. Ann Almgren
