datag.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
[![TravisCI Build Status](https://travis-ci.org/KOLANICH/datag.py.svg?branch=master)](https://travis-ci.org/KOLANICH/datag.py)
![GitLab Build Status](https://gitlab.com/KOLANICH/datag.py/badges/master/pipeline.svg)
[![Coveralls Coverage](https://img.shields.io/coveralls/KOLANICH/datag.py.svg)](https://coveralls.io/r/KOLANICH/datag.py)
![GitLab Coverage](https://gitlab.com/KOLANICH/datag.py/badges/master/coverage.svg)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH/datag.py.svg)](https://libraries.io/github/KOLANICH/datag.py)
[wheel](https://gitlab.com/KOLANICH/datag.py/-/jobs/artifacts/master/raw/wheels/datag-CI-py3-none-any.whl?job=build)

This is a data cleansing, standardization and aggregation framework.

Assumme you have a few noisy bad-quality data tables produced by the ones not caring about their quality. These datasets are made just to say "we support open data", but in fact they have multiple issues.
And we need to train a model on this piece of shit. In order to do it we need to make a candy of shit ..

Issues in scope
---------------

|                               issue                                                           |                      fix                                          |
+-----------------------------------------------------------------------------------------------+-------------------------------------------------------------------+
| data contains typos, even identifiers meant to uniquily identify stuff contain typos!         | custom function fixing the typo                                   |
| data in different units even for the same column                                              | determine unit for each data in the dataset and validate it       |
| some data is completely junk, for example an atom containing 1000 protons or mass in coulombs | detect junk by encorporating domain knowledge and discard it      |
| columns names are semantically incorrect and different datasets use different columns         | rename columns                                                    |
| some columns contain multiple data encoded with some hand-crafted format                      | expand them into different columns, delete the original column    |
| some data field is repeated, but with different values                                        | compute an estimate using the present values or discard the value |
+-----------------------------------------------------------------------------------------------+-------------------------------------------------------------------+

Issues out of scope
-------------------
* Imputation
* (Re)balancing
* encoding
* any stuff doing machine learning (but you can implement it yourself)


Pipeline
--------
* get a formal description on what you want from data to be
    * unit
    * constraints
    * 
* for each source:
	* get a raw record from a source
	* apply a transformation
	* apply in-source validation
* do intersource
	* validation and consistency checks
	* merging and estimation


Task decomposition
------------------
`Spec` - a way to encode requirements to our data.
`Record` - just a dict with some additional properties.
`Source` - gets the records by their identifiers. Has
	`priority`
	`spec`
	`entity`
`Entity` - a way to discover `Source`s providing us with `Record`s of the same kind. Acts as a namespace and as a final validator. Has
	`spec`
`Rule` - transforms the data, detects errors and recovers the missing stuff.
`Disambiguator` - uses a dictionary for standardization of identifiers.
`Merger` - combines different datasets into a composit one.
`Pipeline` - a `Source` of the resulting dataset. Because it is a `Source`, it can be plugged further.


Dependencies
------------
* [```Python >=3.4```](https://www.python.org/downloads/). [```Python 2``` is dead, stop raping its corpse.](https://python3statement.org/) Use ```2to3``` with manual postprocessing to migrate incompatible code to ```3```. It shouldn't take so much time. For unit-testing you need Python 3.6+ or PyPy3 because their ```dict``` is ordered and deterministic.
