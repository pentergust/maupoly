"""Запускает бота.

```
py -m polybot
```
"""

import asyncio

from polybot.bot import main

if __name__ == "__main__":
    asyncio.run(main())
