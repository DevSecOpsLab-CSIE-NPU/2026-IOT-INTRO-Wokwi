import time
print('TEST_PRINT start')
for i in range(3):
    print('tick', i)
    time.sleep(0.5)
print('entering loop')
while True:
    print('alive')
    time.sleep(1)
