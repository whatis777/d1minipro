# This file is executed on every boot (including wake-boot from deepsleep)

# Disable debug output of the board, in order to receive print() messages!
import esp
esp.osdebug(None)

import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()
