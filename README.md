# Sports Data Analysis Project

Contributors: Ben Gunnels, Tim Schneider

## Project Goal

This project will be directed at analyzing live and historical sports performance by gathering different sources of data, exploring unique data hypotheses, providing projection and forecasting, and analyzing player value for a range of sports. The initial stage of the project will focus on publicly available NFL data for fantasy performance projection and ex post facto analysis. In the future the methods produced will be applied to other sports for similar analysis. The results and conclusions of the analysis will be shared via an X (Twitter) account both manually and automatically via API when necessary. 

## Project Structure

> Changes & additions to the structure should be documented here as the project evolves.

| Section        | Path              | Description                                                                                                                                       | Keep Dirty / Clean? | Notes                                 |
|----------------|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|-----------------------------------------|
| Data           | `/data/`          | Temporary data files. Large objects should stay local to your machine.                                                                            | ❌ Clean-up only rarely | Don’t check in big blobs.              |
| Docs           | `/docs/`          | API interface docs, statistical methods, findings, etc.                                                                                          | ✅ Clean             | Update when methods change.            |
| Notebooks      | `/notebooks/`     | Jupyter notebooks for prototyping, data exploration, ad-hoc extraction.                                                                           | ⚠️ Messy allowed     | Good for experiments; disregard polish. |
| Source         | `/src/`           | Main code: APIs, interfaces, helper modules. Each subfolder needs `__init__.py` and explicit exports.                                           | ✅ Clean             | Maintain code quality here.            |
| &nbsp; → Data API | `/src/data_api/` | Contains classes/methods to interact with external data sources / APIs.                                                                          | ✅ Clean             | One interface per source.              |
| &nbsp; → Utils    | `/src/utils/`     | Utility & helper functions used across modules.                                                                                                 | ✅ Clean             | No business logic here.                |
| Tests          | `/tests/`         | Pytest tests. New tests should match naming conventions, live under pytest.ini coverage.                                                           | ✅ Clean             | Keep fast and reliable.                |
| &nbsp; → Data API Tests | `/tests/data_api/` | Tests specifically for the data API interface layer.                                                                                          | ✅ Clean             | Use mocks for external calls.           |

---

### Checklist for Contributors

- [ ] Add new subdirectories under `/src/` with `__init__.py` file.  
- [ ] Explicitly define `__all__` or exports in modules (don’t use wildcard imports).  
- [ ] Update this structure section in README or docs when you introduce new folders.  
- [ ] Ensure tests are added in `/tests/` matching new features or modules.  
- [ ] Maintain `pytest.ini` so it includes any new test paths or settings if structure changes.  
- [ ] Avoid committing large data files (put them in `/data/` but ignore via `.gitignore`).  

## Reference Documentation
Python Yahoo Fantasy API - https://yfpy.uberfastman.com/readme/