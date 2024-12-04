"""Запускает бота.

```
py -m milipoly
```
"""

import asyncio

from milipoly.bot import main

if __name__ == "__main__":
    asyncio.run(main())
