"""Точка входа для запуска бота.

Чтобы запустить бота, воспользуйтесь командой.

```sh
vu run -m polybot
```
"""

import asyncio

from polybot.bot import main

if __name__ == "__main__":
    asyncio.run(main())
