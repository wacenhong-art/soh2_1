# Recovery Provenance

```text
SOURCE_REPOSITORY=soh02
SOURCE_REPOSITORY_PATH=C:\\Users\\ROG\\Documents\\Python\\soh02
SOURCE_COMMIT=dc931f7
SOURCE_COMMIT_FULL=dc931f71be6f92f2895a7b1c26aa3158d3359fab
TARGET_REPOSITORY=soh2_1
RECOVERY_DATE=2026-08-29
RECOVERY_METHOD=git_archive_tracked_tree
SOURCE_GIT_DIRECTORY_COPIED=False
BASELINE_REEXECUTED=False
EXPERIMENT_AUTHORIZED=False
TestLoaded=False
```

This repository is a new working-tree recovery from the complete tracked
snapshot of `soh02@dc931f7`. It was not copied from the current `soh02` HEAD,
and no source `.git` metadata was transferred.

## Historical-result boundary

The source commit records a historical strong supervised baseline:

| Battery | Historical R² |
|---|---:|
| B0007 | approximately 0.966 |
| B0018 | approximately 0.987 |

These are `HISTORICAL_RESULT_FROM_SOURCE_COMMIT` values only. No model,
baseline, validation, or locked test was run while creating `soh2_1`; these
numbers are not a reproduction claim for this new repository.
