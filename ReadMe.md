datag.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
~~![GitLab Build Status](https://gitlab.com/KOLANICH/datag.py/badges/master/pipeline.svg)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH/datag.py/badges/master/coverage.svg)~~
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH/datag.py.svg)](https://libraries.io/github/KOLANICH/datag.py)
~~[wheel](https://gitlab.com/KOLANICH/datag.py/-/jobs/artifacts/master/raw/wheels/datag-CI-py3-none-any.whl?job=build)~~
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://codeberg.org/KOLANICH-tools/antiflash.py)

**We have moved to https://codeberg.org/KOLANICH-ML/datag.py, grab new versions there.**

Under the disguise of "better security" Micro$oft-owned GitHub has [discriminated users of 1FA passwords](https://github.blog/2023-03-09-raising-the-bar-for-software-security-github-2fa-begins-march-13/) while having commercial interest in success and wide adoption of [FIDO 1FA specifications](https://fidoalliance.org/specifications/download/) and [Windows Hello implementation](https://support.microsoft.com/en-us/windows/passkeys-in-windows-301c8944-5ea2-452b-9886-97e4d2ef4422) which [it promotes as a replacement for passwords](https://github.blog/2023-07-12-introducing-passwordless-authentication-on-github-com/). It will result in dire consequencies and is competely inacceptable, [read why](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).

If you don't want to participate in harming yourself, it is recommended to follow the lead and migrate somewhere away of GitHub and Micro$oft. Here is [the list of alternatives and rationales to do it](https://github.com/orgs/community/discussions/49869). If they delete the discussion, there are certain well-known places where you can get a copy of it. [Read why you should also leave GitHub](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).

---

This is a data cleansing, standardization and aggregation framework.

Assumme you have a few noisy bad-quality data tables produced by the ones not caring about their quality. These datasets are made just to say "we support open data", but in fact they have multiple issues.
And we need to train a model on this piece of shit. In order to do it we need to make a candy of shit ..

Issues in scope
---------------

|                               issue                                                           |                      fix                                          |
| --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| data contains typos, even identifiers meant to uniquily identify stuff contain typos!         | custom function fixing the typo                                   |
| data in different units even for the same column                                              | determine unit for each data in the dataset and validate it       |
| some data is completely junk, for example an atom containing 1000 protons or mass in coulombs | detect junk by encorporating domain knowledge and discard it      |
| columns names are semantically incorrect and different datasets use different columns         | rename columns                                                    |
| some columns contain multiple data encoded with some hand-crafted format                      | expand them into different columns, delete the original column    |
| some data field is repeated, but with different values                                        | compute an estimate using the present values or discard the value |


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
* `Spec` - a way to encode requirements to our data.
* `Record` - just a dict with some additional properties.
* `Source` - gets the records by their identifiers. Has
	* `priority`
	* `spec`
	* `entity`
* `Entity` - a way to discover `Source`s providing us with `Record`s of the same kind. Acts as a namespace and as a final validator. Has
	* `spec`
* `Rule` - transforms the data, detects errors and recovers the missing stuff.
* `Disambiguator` - uses a dictionary for standardization of identifiers.
* `Merger` - combines different datasets into a composit one.
* `Pipeline` - a `Source` of the resulting dataset. Because it is a `Source`, it can be plugged further.
