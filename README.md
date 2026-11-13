# Duo simulator screenshot probe

A minimal experiment to capture Apple Settings on the official iPhone Duo simulator in a GitHub-hosted Mac. No third-party app code, user data, or credentials are uploaded. Output is simulator evidence, not a physical-device capture. Workflow runs only by manual dispatch, with a 12-minute cap and three-day artifact retention. This experiment does not establish permission to republish Apple interface screenshots.

## Verified result (2026-11-13)

The iOS 27.2 run produced a valid 1398 x 2034 Settings screenshot on the outer display. The inner capture was black; unfolded capture has not been verified. The overall first run was cancelled after capture and artifact upload had succeeded. A second iOS 27.1 run timed out during bootstatus after 120 seconds. Current parameters prefer the newer runtime and allow six minutes for cold boot; those final parameters have not been rerun. This is a proof of one successful capture, not a stable full-app capture service.
