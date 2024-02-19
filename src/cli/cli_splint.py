import logging

import splint

logging.basicConfig(level=logging.DEBUG)

s = splint.SplintPackage(folder="./src", env=splint.SplintEnvironment())
logging.info(f"Loaded {s.module_count} modules")

results = s.run_all()

for i, result in enumerate(s.run_all(), start=1):
    logging.info(f"Result {i}: {result}")
