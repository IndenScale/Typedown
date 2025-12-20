# Main Entry

Importing the math config from the library.

```config:python
# This import is expected to fail currently because '@lib' resolution is not implemented
from @lib.math import MathConfig
```

Defining an entity using the imported type.

```entity:MathConfig
id: main_config
precision: 2
mode: "decimal"
```
